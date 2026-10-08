import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import hudson.plugins.git.BranchSpec
import java.util.Collections

def jenkins = Jenkins.getInstance()
def jobName = "TaskFlow-CI-CD"

def job = jenkins.getItem(jobName)
if (job == null) {
    job = jenkins.createProject(WorkflowJob.class, jobName)
    println("--> [INIT] Created project ${jobName}")
}

def repoUrl = "https://github.com/Kalana-beep/taskflow.git"
def branchSpec = new BranchSpec("*/main")
def remoteConfig = new UserRemoteConfig(repoUrl, null, null, null)
def scm = new GitSCM(
    Collections.singletonList(remoteConfig),
    Collections.singletonList(branchSpec),
    false,
    Collections.emptyList(),
    null,
    null,
    Collections.emptyList()
)
def definition = new CpsScmFlowDefinition(scm, "Jenkinsfile")
definition.setLightweight(true)
job.setDefinition(definition)
job.save()
println("--> [INIT] Configured ${jobName} from SCM: ${repoUrl}")
