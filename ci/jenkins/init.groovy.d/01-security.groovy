import jenkins.model.*
import hudson.security.*

def instance = Jenkins.getInstance()

// Configure security realm with local admin account
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount("admin", "admin")
instance.setSecurityRealm(realm)

// Enable open local authorization strategy for automated CI execution
instance.setAuthorizationStrategy(new AuthorizationStrategy.Unsecured())

// Disable CSRF protection for local automated API triggering
instance.setCrumbIssuer(null)

// Set Jenkins root URL
def location = jenkins.model.JenkinsLocationConfiguration.get()
if (location != null) {
    location.setUrl("http://localhost:8080/")
    location.save()
}

instance.save()
println("--> [INIT] Jenkins security, CSRF bypass, and root URL configured.")
