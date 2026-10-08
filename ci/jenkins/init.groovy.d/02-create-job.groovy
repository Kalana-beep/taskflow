import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition
import java.io.File

def jenkins = Jenkins.getInstance()
def jobName = "TaskFlow-CI-CD"

def job = jenkins.getItem(jobName)
if (job == null) {
    job = jenkins.createProject(WorkflowJob.class, jobName)
    println("--> [INIT] Created project ${jobName}")
}

File jf = new File("/workspace/Jenkinsfile")
if (jf.exists()) {
    def definition = new CpsFlowDefinition(jf.text, true)
    job.setDefinition(definition)
    job.save()
    println("--> [INIT] Loaded Jenkinsfile from /workspace/Jenkinsfile into ${jobName}")
} else {
    println("--> [INIT] /workspace/Jenkinsfile not found yet.")
}
