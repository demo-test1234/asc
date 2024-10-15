import os
import time

from aigcpanel.base.util import rootDir, datetimeRandomName, datetimeRandomNameParseTimestamp

JOBS = {}

JOB_LIMIT = 1
OUTPUT_DIR = rootDir('aigcpaneloutput')

os.makedirs(OUTPUT_DIR, exist_ok=True)


def runningCount():
    count = 0
    for jobId, job in JOBS.items():
        if job['status'] == 'running':
            count += 1
    return count


def overCount():
    return runningCount() >= JOB_LIMIT


def get(jobId):
    return JOBS.get(jobId)


def create(jobData):
    jobId = datetimeRandomName()
    JOBS[jobId] = {
        "status": "running",
        "start": time.time(),
        "end": None,
        "msg": None,
        "data": jobData,
    }
    cleanJobs()
    return jobId


def updateFail(jobId, msg):
    JOBS[jobId]["status"] = "fail"
    JOBS[jobId]["end"] = time.time()
    JOBS[jobId]["msg"] = msg


def updateSuccess(jobId, data):
    JOBS[jobId]["status"] = "success"
    JOBS[jobId]["end"] = time.time()
    JOBS[jobId]["data"] = data


def outputPath(file):
    return os.path.join(OUTPUT_DIR, file)


def cleanJobs():
    # clean expire jobs
    expire = 60 * 60 * 24
    for jobId, job in JOBS.items():
        if job['status'] == 'success' and time.time() - job['start'] > expire:
            del JOBS[jobId]
    # clean output files
    for file in os.listdir(OUTPUT_DIR):
        ts = datetimeRandomNameParseTimestamp(file)
        if ts and time.time() - ts > expire:
            os.remove(os.path.join(OUTPUT_DIR, file))
