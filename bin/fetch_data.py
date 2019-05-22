import gitlab
import argparse
import json
import tempfile
import zipfile
import filecmp
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description='Fetch files from gitlab')
parser.add_argument('--url', dest='url', required=True,
                    help='GitLab root URL')
parser.add_argument('--token', dest='token', required=True,
                    help='GitLab token')
parser.add_argument('--config', dest='config', required=True,
                    help='Configures which files to fetch')

args = parser.parse_args()
with open(args.config, "r") as cfgFile:
    config = json.loads(cfgFile.read())
    gl = gitlab.Gitlab(args.url, private_token=args.token)
    gl.auth()

    for task in config:
        projectId = task["project"]
        project = gl.projects.get(projectId)
        pipelines = project.pipelines.list(ref=task["branch"], status='success')
        # Find last pipeline
        pipelines = sorted(pipelines, reverse=True, key=lambda x: x.id)
        pipelineIndex = 0
        if 'nth' in task:
            pipelineIndex = task['nth']
        if pipelineIndex < len(pipelines):
            print ("Pipeline for project " + project.name + " on branch " + task["branch"] + " is " + str(pipelines[pipelineIndex].id) + " for commit " + pipelines[pipelineIndex].sha)
            pipeline = pipelines[pipelineIndex]
            for job in pipeline.jobs.list():
                if job.name == task["job"]:
                    with tempfile.TemporaryFile(mode="w+b") as file:
                        job = project.jobs.get(job.id)
                        job.artifacts(streamed=True, action=file.write)
                        zip = zipfile.ZipFile(file)
                        for file in zip.filelist:
                            if file.filename.endswith(".json"):
                                content = zip.read(file)
                                with tempfile.NamedTemporaryFile(mode="w+b", delete=False) as file2:
                                    file2.write(content)
                                    file2.flush()
                                    file2.close()
                                    if Path(task["dest"]).is_file():
                                        if not filecmp.cmp(file2.name, task["dest"]):
                                            print ("File has changed!")
                                            shutil.copyfile(file2.name, task["dest"])
                                    print ("File is new!")
                                    shutil.copyfile(file2.name, task["dest"])
