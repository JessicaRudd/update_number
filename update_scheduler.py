import os
import random
from datetime import datetime
from google.cloud import scheduler_v1
from google.protobuf import timestamp_pb2
import google.auth

def update_schedule(request):
    try:
        print("Scheduler function started")
        # Get the project ID and job ID from environment variables
        project_id = os.environ.get("GCP_PROJECT")
        job_id = os.environ.get("SCHEDULER_JOB_NAME")
        location_id = os.environ.get("GCP_LOCATION")
        # Initialize Cloud Scheduler Client
        credentials, project_id = google.auth.default()
        client = scheduler_v1.CloudSchedulerClient(credentials=credentials)

        # Generate random hour and minute
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)

        # Build Cron Expression
        cron_expression = f"{random_minute} {random_hour} * * *"
        print(f"New cron schedule: {cron_expression}")

        # Build Job Path
        job_path = client.job_path(project_id, location_id, job_id)
        
        # Get the current schedule
        job = client.get_job(request={"name": job_path})
        print(f"Current schedule: {job.schedule}")

        # Update Schedule
        job.schedule = cron_expression
        # Create timestamp
        now = datetime.now()
        next_run = datetime(year=now.year, month=now.month, day=now.day, hour=random_hour, minute=random_minute)
        if next_run <= now:
          next_run = datetime(year=now.year, month=now.month, day=now.day+1, hour=random_hour, minute=random_minute)

        next_run_timestamp = timestamp_pb2.Timestamp()
        next_run_timestamp.FromDatetime(next_run)
        job.schedule_time = next_run_timestamp
        # Update job request
        update_job_request = scheduler_v1.UpdateJobRequest(job=job)
        
        #Update the job
        updated_job = client.update_job(request=update_job_request)
        print(f"Updated schedule: {updated_job.schedule}")
        print(f"Updated next run time: {updated_job.schedule_time}")
        print("Scheduler function completed")

        # Trigger number update function
        # Set function to trigger our number updater
        import requests
        function_url = os.environ.get("NUMBER_UPDATE_URL")
        response = requests.post(url=function_url)
        print(f"Number update function called. Status code {response.status_code}")


        return 'Success'
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
   
    update_schedule(None)