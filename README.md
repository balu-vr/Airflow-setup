# Airflow setup on ECS

**Overview**
-	Apache Airflow is Deployed with Containerization using docker to enhance scalability and availability of the service to orchestrate and schedule DataEngineering pipelines to run in batch process.
-	The Airflow is tightly integrated with GIT for CI/CD of DAG migration from Azure Git repository. This supports seamless deployment and versioning of code on GIT.
-	The Airflow database is backed by Amazon RDS Postgresql to enable the capabilities of DAG, connection management and parallel execution of DAGs in Prod environment.
-	Leveraged AWS ECS with Fargate to bring up the serverless service to minimize operational efforts needed to manage the infrastructure. 
**End to end setup**:

  <img width="800" height="201" alt="image" src="https://github.com/user-attachments/assets/e3c8a622-ce79-4ca8-8e7a-f986b08dc3a0" />

 
**Dependencies** 
- Create all the necessary files needed to setup ECS on AWS. 
- The Dockerfile below is composed of all the dependencies to enable Airflow 2.9.2 service backed by Python3.9 to orchestrate batch jobs.
    - Apache Airflow 2.9.2
    - Python3.9
    - Psycopg2 for Postgres connection
    - Pem files to connect to EC2 servers as needed
    - GIT 
    - A DAG to sync the Airflow DAGs from GIT to container location

**Dockerfile:**
    # Use the official airflow image
    FROM apache/airflow:2.9.2-python3.9
    
    # Install psycopg2
    RUN pip install psycopg2-binary
    
    #Copy airflow config file to container 
    COPY airflow.cfg /opt/airflow/airflow.cfg
    
    #Copy pem files of ec2 servers where the Data Engineering pipelines reside 
    COPY linux.pem /opt/airflow/linux.pem
    COPY Oregon.pem /opt/airflow/Oregon.pem
    
    # Switch to root user to install Git and enable container to sync DAGs on GIT repo
    USER root
    
    # Install Git
    RUN apt-get update && apt-get install -y git openssh-client
    
    # Copy the SSH keys into the container. These are needed for Azure git authentication
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
    
    #Execute only if we want to force refresh dags from git 
    RUN rm -rf /opt/airflow/dags/* && git clone git@ssh.dev.azure.com:v3/devops/DEA/dag-composer /opt/airflow/dags
    
    #Copy dag sync file to airflow 
    COPY prod_dag_sync.py /opt/airflow/dags/
    
    # Copy the entrypoint script into the image
    COPY entrypoint.sh /usr/local/bin/entrypoint.sh
    
    # Set the entrypoint to the script
    ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
    
    #Expose the webserver port 
    EXPOSE 8080
     
**Entrypoint File**: A shell script called Entrypoint.sh file will be executed on the container to initiate the Airflow service.
    - Refer to Entrypoint.sh file in the repo
 
**Airflow configuration**
  - The configurations are defined in the airflow.cfg that contains following sections:
    - Core: DAG Path and Executory type
    - Database: Connections pointing to database (Define postgres connection in this case)
    - Email and Webserver: email server and webserver server details with IP and port information
    - Refer to the file airflow.cfg file in the repo
 
**Elastic Container Service**
 - The AWS ECS setup is needed to run the docker image as a ‘Service’ on ECS cluster.
**Components** 
    - Create an ECS Cluster ‘DataEngineering_Airflow’
         - ECS Task Definition :
            - Name: airflow_task
            - Launch Type: Fargate
            - Task Size - 2 vCPU, 8 GB Memory
         - Container Details:
            - Provide image URI
         - Port Mapping
            - Container port : 8080
            - Protocol: TCP
         - Specify Container level CPU and Memory
         - Specify Ephemeral Storage needed for container
         - Specify other properties like log location, health metrics, Environment variables
         - Create Service:
         - Launch Type: Fargate
         - Application Type: Service
         - Family: airflow_task
         - Service Name: Airflow_service_v2
         - Desired Tasks: 2
         - Deployment Type: Rolling update
        - [Optional]Load Balancing: Choose ALB and the Target Group where the ALB is created
        - Networking: Choose VPC (Boomi - Prod/Dev - TFS) and Security Groups


**Service running in ECS**:

  <img width="800" height="400" alt="image" src="https://github.com/user-attachments/assets/ce19c869-b445-498b-95c4-15ba369e51a9" />

   
**GIT Integration for CI/CD**:
- The Airflow setup will be tightly integrated with Azure GIT repository ‘ex: dag-composer’ to sync all the DAGS.
  - Generate keys on the local machine: ssh-keygen -t rsa 
  -	Navigate to Azure GIT → User Settings → SSH Public keys → New Key → Copy paste the public key generated from the above step
  -	Copy the public and private key files to the container under /root/.ssh
  -	Assign right permissions to the keys as defined in Dockerfile
  -	Copy the dag files from git repo to /opt/airflow/dags/ executing ‘git clone’ on the container which will execute when the image is setup on ECS service for the first time or when updated again.
  RUN rm -rf /opt/airflow/dags/* && git clone git@ssh.dev.azure.com:v3/devops/DEA/dag-composer /opt/airflow/dags
  -	Created DAG ‘prod_dag_sync’ to sync the airflow dags from GIT to the airflow dag location on hourly basis. 
  -	This will keep track of new changes added to GIT repository and pull them into Airflow automatically.

**Sync DAGs from Repo to container**:
  - Refer script to syncup DAGs from GIT environment to Container git_sync.pyin repo 
 
**Steps to Setup Airflow on ECS**
1.	Setup Docker on your machine 
2.	Create the below prereq files:
a.	airflow.cfg with customized configuration
b.	entrypoint.sh used to initiate Airflow on the container
c.	Public and private SSH keys for GIT authentication with Azure repo.
3.	Create Airflow folder on your local machine and navigate to it from your terminal
4.	Create DockerFile as defined in DockerFile section 
5.	Build the docker image from the DockerFile using ‘docker build’ command
6.	Run the docker image locally using ‘docker run’ to do the following.
    a.	Validate the service is installed successfully 
    b.	Set up admin login to connect to Airflow
      i.	docker exec -it airflow /bin/bash
      ii.	airflow users create --username admin --firstname xxxx --lastname xxxx --role Admin --email xxxx@xxxx.com --password xxxx
      iii.	exit
    c.	Test the service by connecting to Airflow UI using ‘localhost:8080’ 
7.	Stop the service on local
8.	Create necessary AWS services to run Airflow on ECS
a.	Create the Elastic Container Registry on AWS where the docker images can be stored and provide necessary authentication for the users to push the docker images from local repository to ECR
b.	Create Elastic Container Service where the docker images run based on the configs defined
c.	[optiopnal] Set up Application Load blancer on AWS with Target Groups to have a permanent url – (Ex: https://de-airflow.company.net/ )
9.	Install AWS CLI and configure it with AWS keys 
10.	Push the docker image to ECR using the commands defined in AWS ECR (ECR → Select Repository → View push commands) .
11.	Navigate to ECS and create a Task Definition by specifying the URI of the image and the capacity needed.
12.	Navigate to ECS cluster and create service and provide the task definition and define the configuration to execute Fargate ECS service.

