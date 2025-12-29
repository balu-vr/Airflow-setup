#Use the official airflow image
FROM apache/airflow:2.9.2-python3.9

# Install psycopg2
RUN pip install psycopg2-binary

#Copy customer airflow to container 
COPY airflow.cfg /opt/airflow/airflow.cfg

#Copy pem files of ec2 servers 
#Servers on which the DAGs trigger airflow jobs
COPY linux.pem /opt/airflow/linux.pem
COPY Oregon.pem /opt/airflow/Oregon.pem


# Switch to root user
USER root

# Install Git
RUN apt-get update && apt-get install -y git openssh-client

# Copy the SSH keys into the container. These are needed for Azure git autnetication
COPY id_rsa /root/.ssh/id_rsa
COPY id_rsa.pub /root/.ssh/id_rsa.pub

# Set permissions for the SSH keys and pem files
RUN chmod 600 /root/.ssh/id_rsa && chmod 644 /root/.ssh/id_rsa.pub
RUN chmod 600 /opt/airflow/linux.pem
RUN chmod 600 /opt/airflow/Oregon.pem

# Add Azure DevOps SSH host to known_hosts to avoid host verification issues
RUN mkdir -p /root/.ssh && ssh-keyscan ssh.dev.azure.com >> /root/.ssh/known_hosts

# Set permissions for SSH directory and known_hosts
RUN chmod 700 /root/.ssh && chmod 644 /root/.ssh/known_hosts

#Execute only if we want to force refresh dags from git "GIT repo name: dag-composer"
RUN rm -rf /opt/airflow/dags/* && git clone git@ssh.dev.azure.com:v3/intappdevops/DEA/dag-composer /opt/airflow/dags

# Set ownership to airflow user for DAGs and SSH keys
#RUN chown -R airflow /opt/airflow/dags /root/.ssh

#Copy dag sync file to airflow 
COPY prod_dag_sync.py /opt/airflow/dags/

# Copy the entrypoint script into the image
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

#Expose the webserver port 
EXPOSE 8080
