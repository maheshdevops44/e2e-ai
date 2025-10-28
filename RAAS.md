# Roles as a Service Documentation

## Table of Contents
1. [Purpose](#purpose)
2. [RaaS Structure](#raas-structure)
3. [RaaS Managed Policies](#raas-managed-policies)
    * [Securing Actions Using Conditions](#securing-actions-using-conditions)
    * [RaaS Managed Policy Mapping](#raas-managed-policy-mapping)
    * [RaaS Managed Policy Development FAQs](#raas-managed-policy-development-faqs)
4. [RaaS Roles](#raas-roles)
    * [RaaS Role Development FAQs](#raas-role-development-faqs)
    * [RaaS Runner Structure](#raas-runner-structure)
5. [RaaS Automation](#raas-automation)
    * [RaaS Automation FAQs](#raas-automation-faqs)
6. [Utilizing RaaS in lower environments](#utilizing-raas-in-lower-environments)
7. [Merge Request Approval Process](#merge-request-approval-process)
8. [Off Hours Merge Request Approval Process](#off-hours-merge-request-approval-process)


## Purpose

| Video Link | Description |
| ---------- | ----------- |
| <a href="https://cigna.rev.vbrick.com/#/videos/8819cd2f-53d2-4f5e-877c-e2449d7b5a5c"><img src="https://github.sys.cigna.com/cigna/coe-edu-videos/blob/main/button-images/green_round_play_button.jpeg" width="100" height="100"/></a> | Learn the basics; What is RaaS, how does it help me? |
| <a href="https://cigna.rev.vbrick.com/#/videos/b5d81ea2-9353-4a67-b9b5-a4d166fbfed5"><img src="https://github.sys.cigna.com/cigna/coe-edu-videos/blob/main/button-images/green_round_play_button.jpeg" width="100" height="100"/></a> |  High-level overview of RaaS folder structure and content |
| <a href="https://cigna.rev.vbrick.com/#/videos/631fae30-dd2f-4489-aaa9-ea07f39a078a"><img src="https://github.sys.cigna.com/cigna/coe-edu-videos/blob/main/button-images/green_round_play_button.jpeg" width="100" height="100"/></a> | Detailed description on the contents of roles directory |
| <a href="https://cigna.rev.vbrick.com/#/videos/bd1d9616-79a9-4c86-a62c-8fe117d5f86b"><img src="https://github.sys.cigna.com/cigna/coe-edu-videos/blob/main/button-images/green_round_play_button.jpeg" width="100" height="100"/></a> |  Detailed description on the contents of managed_policies directory |
| <a href="https://cigna.rev.vbrick.com/#/videos/5fca6e18-475a-4e0b-90e7-8cf2fc988843"><img src="https://github.sys.cigna.com/cigna/coe-edu-videos/blob/main/button-images/green_round_play_button.jpeg" width="100" height="100"/></a> |  Detailed description on the contents of mappings.yml file |
| <a href="https://cigna.rev.vbrick.com/#/videos/44e636b8-c258-4e36-8335-f8cb3a20a500"><img src="https://github.sys.cigna.com/cigna/coe-edu-videos/blob/main/button-images/green_round_play_button.jpeg" width="100" height="100"/></a> |  Detailed description on the contents of .targets.yml file |

## RaaS Structure
The RaaS project follows a linear directory structure at the root of the project.

| Name | Type | Description | Created By Users | Modified By Users |
|--|--|--|--|--|
| your-account-name or your-project-name | Directory | A directory for the roles and policies required by your account or project.  This directory will contain a subdirectories for managed policies and roles | Yes | Yes |
| .targets.yml | CI/CD configuration | Mapping of accounts and environments to folder(s) | No | Yes |
| README.md | Readme | Readme for code | No | No | 

## Raas Managed Policies

    ---
    statements:
    -
      effect: "Allow"
      actions:
      - iam:CreatePolicy
      - iam:CreatePolicyVersion
      - iam:DeletePolicy
      - iam:DeletePolicyVersion
      - iam:ListPolicyVersions
      resources:
      - "arn:aws:iam::929468956630:policy/CentralizedLogging*FirehosePolicy"
      - "arn:aws:iam::929468956630:policy/CentralizedLogging*LogPolicy"
    - 
      effect: "Allow"
      actions:
      - "ec2:RebootInstances"
      - "ec2:StartInstances"
      - "ec2:StopInstances"
      - "ec2:DescribeInstanceStatus"
      resources: 
      - "arn:aws:ec2:us-east-1:*:instance/*"
      condition:
        StringEquals:
          ec2:resourceTag/purpose:
          - "AudioDataScience"


Each managed policy yml must contain at least one statement block containing the following nodes:
* Effect - Typically Allow or Deny to explicitly indicate the inclusion or exclusion of the rights from the listed resources in the stanza
* Actions - One or more AWS policies that will be either allowed or disallowed from the listed resources
*  Resources - One or more resources impacted by the stanza
*  Condition - A set of conditions bound to the actions on the resources.  Use this to limit your actions on resources!

### Securing Actions Using Conditions

In order to ensure that our RaaS created roles and policies are as secure as possible, it is highly recommended to leverage the use of conditions where applicable.  For example, any IAM calls that include Create/Delete/Attach should be accompanied with a Condition to isolate those actions to specific policies.

```
-
    effect: "Allow"
    actions:
    - iam:AttachRolePolicy
    resources:
    - !Sub  "arn:aws:iam::${AWS::AccountId}:role/CentralizedLogging*LogRole"
    - !Sub  "arn:aws:iam::${AWS::AccountId}:role/CentralizedLogging*S3DeliveryRole"
    - !Sub  "arn:aws:iam::${AWS::AccountId}:role/CentralizedLogging*LambdaRole"
    condition:
    ForAnyValue:ArnEquals:
        iam:PolicyArn:
        - !Sub  "arn:aws:iam::${AWS::AccountId}:policy/CentralizedLogging*FirehosePolicy"
        - !Sub  "arn:aws:iam::${AWS::AccountId}:policy/CentralizedLogging*LogPolicy"
```

The stanza above is a proper example of how to isolate an 'AttachRolePolicy' on specific roles to specific policy values.  This will prevent my RaaS role from deleting any policy that doesn't follow the Arn values listed in the Condition section.

### RaaS Managed Policy Mapping

Mappings (or how to use variables with RaaS)  
- Mappings is a native cloudformation functionality to allow varible use depending on where a template is run
- This is used by RaaS to provide a means of specificying a certain resource per enviornment in order to follow least privilege
- The RaaS code will look for a mappings.yml file existing in the base directory (ex: security, digexp etc)
- The account number is used as a key to define what values the varibles hold

Sample mappings.yml file:
```
---
053357076836:
  bucketname: dev-bucket
  bucketname2: dev-bucket2
053357076835:
  bucketname: prod-bucket
  bucketname2: prod-bucket2
```
Leveraging the mapped values
- In order for a policy to leverage the mapping values a cloudformation intrinsic function is used
- RaaSMap is a static name of the mapping section created by internal code

Sample function usage in policy document:
```
resources:
- !FindInMap [RaaSMap, !Ref "AWS::AccountId" , bucketname]
```


### RaaS Managed Policy Development FAQs
##### Are there any naming conventions for Policies?
* Policy names must be unique, and must not match any pre-existing AWS managed policies

##### Can I include an all inclusive resource for my policies?
It is highly encouraged that your policies isolate rights to strict resources.  Set/Apply/Create based policies will typically be rejected if they are applied to all-all resources (i.e. *)

##### Can My Resources Contain Wildcards
Yes, however your wildcards should be as strict as possible, specifically isolating the policy to a pattern specific to your resources.  See above for examples

## RaaS Roles

There are two formats for Roles in Roles as a Service. The first format (v1) is described below. This format allows you to attach custom managed policies. The second format is the v2 role. This format is documented [here](https://confluence.sys.cigna.com/display/CLOUD/RaaS+-+V2+Roles) and lets you leverage canned policies along with attaching custom managed policies to the role. For documentation on the v2 role and canned policies please view the confluence page.

### V1
    ---
    managedPolicyArns:
    -
      name: Enterprise/GoldenAmiRequirements
      cignamanaged: true

    -
      name: CentralizedLoggingCFTIAMRequirements
      awsmanaged: false
    -
      name: CentralizedLoggingRunnerPolicies
      awsmanaged: false
    -
      name: AmazonEC2ReadOnlyAccess
      awsmanaged: true

    federated: true
    max_duration: 3600
    additionalTags:
      MyCustomTag: MyCustomTagValue
      MyCustomTag2: MyCustomTagValue2

Each Role yml must contain at least one managed policy block which contains the name of the policy, and if it is aws managed or not.
* Name - This name must match the name of your managed policy yml file if you are leveraging a custom policy.  If you specify an aws managed policy, the policy must match the naming of the policy within AWS
* awsmanaged - If false, RaaS will look into your managed_policies path for the policy name.  If true, RaaS will look for the policy within the AWS managed policies (ex: job-function/Billing would map to arn:aws:iam::aws:policy/job-function/Billing).
* cignamanaged - If false, RaaS will look into your managed_policies path for the policy name.  If true, RaaS will look for the policy within the AWS account managed policies (ex: Enterprise/GoldenAMIRequirements would map to arn:aws:iam::aws:policy/Enterprise/GoldenAMIRequirements).  
Here is a list of the available Cigna managed policies:

     | Name | ARN Map|
     |--|--|
     | Enterprise/GoldenAMIRequirements | arn:aws:iam::${AWS::AccountId}:policy/Enterprise/GoldenAmiRequirements |
     | Enterprise/GoldenVPCRequirements | arn:aws:iam::${AWS::AccountId}:policy/Enterprise/GoldenVpcRequirements |
**PLEASE NOTE** this is only an example. The GoldenVPC and GoldenAMI policies are no longer deployed separately and instead you should use their related [canned policies](https://confluence.sys.cigna.com/display/CLOUD/RaaS+-+Canned+Policies).
* additionalTags - This key should contain a map of keys and values for tags you want to apply to your RaaS resource. In the example above we would be adding 2 tags to our created Role `MyCustomTag` and `MyCustomTag2` would be the names with `MyCustomTagValue` and `MyCustomTagValue2` values respectively.
A role may specify a max_duration if the process leveraging the role requires longer than a one hour duration. This is discouraged for interactive use cases

There are three types of roles(**a role can only have one type**): federated, cross account, and service.
The federated node indicates that the role that is being created is allowed for console use/saml login.
Additionally cross account and service roles are supported.
Service roles require the name as it would appear in a trust policy

```
cross_account:
    account: 000000000000
    role: Project-Env-STS (optional)
    external_id: 8667fc0c-1b93-494c-8fb0-727ba676f08c (optional)

service: lambda
```

### RaaS Role Development FAQs
##### What is a federated role?
A federated role allows a user to log into the AWS console using the new role provisioned through RaaS.  This is similar to the initial role you were provided when you first received access to AWS.
##### Do federated roles follow a naming convention
Yes, all federated roles must be fully capitalized.  For example, DBSUPPORT.  Roles that do not follow this convention will have their merge request denied.
#### What does RaaS check for as part of the pipeline?
* Overly permissive policies (ex service:*)
* Federated roles require that the role names be fully capitalized
* Do not include the word 'Role' in the name of your role
* Multiple role type definitions (service, federated, cross account) when only one can be chosen
* This is the regular expression used to validate role & policy names: `format: ^[a-zA-Z][a-zA-Z0-9]+$"}`
* The federated role name cannot match any of the following names: "AccountAdmin","DatabaseAdmin","CloudAdmin","NetworkAdmin","SystemAdmin","IdentityAccessAdmin","StorageAdmin","Support","SupportAdmin","Developer","AnalyticsDeveloper","MobileDeveloper"
#### What is the branching strategy of this repository?
The default branch is main, dev branches should be off of it. To promote to test and prod environments, create a PR from your dev branch into main. Once the PR is merged into main your test and prod environments will be deployed.
#### Account Whitelisting
[doc](https://confluence.sys.cigna.com/display/CLOUD/RaaS+-+Account+Whitelisting)  
If you get an error from conftest saying your account is not allowed to access another account, please do the following:
- Verify that access is needed
- Reach out in the RaaS channel with your account ID, the account ID you're trying to access, as well as documentation/rationale for why you need that access. 


### RaaS Targets Structure
For the CI runner to create your roles, a stanza will need to be added to the .targets.yml file within RaaS.  Simply add our account(s) to the accounts block, and add your directory or directories to the directories block to inform the CI process of where your roles are to be created.

```
#The accounts block maps account names to account numbers.  
#This tells the Jenkins process where to deploy your role(s).
accounts:
  cigna-us-sysmgmt-eng-dev: '929468956630' 

#The directories block maps directories to your account.  
#The following block maps the alarm-funnel directory to the 
# cigna-us-sysmgmt-eng-dev and cigna-us-sysmgmt accounts, respectively.
directories:
  alarm-funnel:
    dev:
    - cigna-us-sysmgmt-eng-dev
    prod:
    - cigna-us-sysmgmt
    test: []

```

## RaaS Automation
### RaaS Automation FAQs
##### Where do I begin?
* First start by cloning the 'main' branch of RaaS
> git clone git@github.sys.cigna.com:cigna/aws-roles-as-a-service.git

or

> git clone -b main https://github.sys.cigna.com/cigna/aws-roles-as-a-service.git
* Next, cd into the RaaS directory, and create a new branch
> cd roles-as-a-service

> git checkout -b mynewbranch
* Get started by creating a directory for your account.  This directory should typically match the account name pattern assigned in AWS.  Create the policies and role directory as well
> mkdir cigna-us-myaccount

> mkdir cigna-us-myaccount/managed_policies

> mkdir cigna-us-myaccount/roles
* Follow the [guidelines](https://github.sys.cigna.com/cigna/aws-roles-as-a-service/wikis/home#raas-managed-policy-development-faqs) on this page to create the respective roles and policies for your account.  Once your are ready, make an initial commit to push your branch to the repository
> git commit -a -m "Adding cigna-us-myaccount, initial commit"

> git push origin mynewbranch
* Now that your roles and policies are created in RaaS, you need to modify the .targets.yml to add a mapping to kick off the automation for your account. 

##### Where does the automation live?
The RaaS pipeline configuration can be found here [https://orchestrator9.orchestrator-v2.sys.cigna.com/job/orchestrators-folders/job/roles-as-a-service/job/RaaS-Pipeline/](https://orchestrator9.orchestrator-v2.sys.cigna.com/job/orchestrators-folders/job/roles-as-a-service/job/RaaS-Pipeline/)

##### I am ready to test in my dev account
* Once your branch and your modifications to the .targets.yml file have been created and pushed to the repository, the automation job will fire.  You can [click here](https://orchestrator9.orchestrator-v2.sys.cigna.com/job/orchestrators-folders/job/roles-as-a-service/job/RaaS-Pipeline/) and into your branch to see the progress

##### I am ready to deploy to the test account
* Once you are happy with your results from your manual CI/CD run (above), you can request a merge request from your branch to the 'main' branch.
* Merge requests no longer require manual review (except during the annual stability period).  A RaaS bot will automatically review a PR after a build to ensure that is succeeded and merge the changes automatically into the `main` branch
* Once the PR is merged, and the branch contents are merged to 'main', the CI/CD will run an automated job that deploys all changes to your projects test and production AWS accounts

##### I created a federated role, what do I do next?
* Once the automation has run for the respective environment, a global group will be created for the federated role against the account specified.
* Requests for Global group creations occur every 3 hours.  All groups go through Ownership Approval process via Service Now.
* Once the global group has been created, it will be available in Saviynt in 2 to 3 business days.  Account or Group Owner approval is required to see the group in Saviynt, so if you do not see your group after 2 business days, follow up with the account owner to look for any Service Now requests requiring approval.
* You can see any issues or progress of the global group creation within the [Roles as a service Webex group](https://eurl.io/#YkMCv59_X)

##### Why can't I request access for my new federated role global group in ARS? (USM only)
* Global groups requests for USM users switched from Aveksa to Saviynt in 2023
* The new process requires owner metadata for the group to be added within a secondary step, along with additional nightly batch steps
* Expect the process to take up to an additional 2 days after the group is created for the group to be requestable in Saviynt

##### My federated role and global group was created.  Is there anything else that needs to happen before it appears in ARS?
* In the previous FAQs you can see how to confirm the federated IAM role global group was created
* Once you confirm this, there will be an automated request made by `P-AUTOGSAAWS` to the global group owners to update group metadata as it syncs to the ARS system
* You can see an example of this request here: [Entitlement Metadata and Ownership Update Request](https://cigna.service-now.com/sc_req_item.do?sys_id=d390a31287ba8a5c5c1855b83cbb352f)
* To a record of this request, you can view all requests made by `P-AUTOGSAAWS` the via global [ServiceNow search](https://cigna.service-now.com/now/nav/ui/classic/params/target/sc_request_list.do%3Fsysparm_query%3D123TEXTQUERY321%253DP-AUTOGSAAWS%26sysparm_first_row%3D1%26sysparm_view%3D)
* In the query linked above, you can filter by the account owner (NOTE it is not the backup owner) to view all the requests pending or completed
* Further, filter by the dates when the global group was created to find the exact match.  Within the ticket, click on the RITM and verify that all the `Approvers` listed at the bottom have approved the group metadata ticket

## Utilizing RaaS in lower environments
##### Pattern for using internal ids in CPC lower environments
* Utilize the username/password for the (lower environment) internal ids in the lower environment servers
* Make sure the server is whitelisted for your internal ids (ask CPC to enable you on this)
* Use aws-fed to federate with AWS and populate your credentials file

##### Pattern for ISG servers:
* Utilize the username/password for the (lower environment) internal ids in the lower environment servers
* Make sure the server is whitelisted for your internal ids
* Use aws-fed to federate with AWS and populate your credentials file

## Merge Request Approval Process 
* Confirm the identity of the user requesting the merge. Are they a regular contributor who is known to contribute to the account they are modifying? If not, vet further.
* Confirm the roles and policies being requested follow least privilege. Note that RaaS doesn't allow for wildcard requests.
* Requires 3 maintainers to approve.

## Off Hours Merge Request Approval Process
* There are some scenarios where a request cannot wait until the next business day. For example, if a team is in the middle of a release and need to perform a backout, only to find out their deployer role does not have permission to perform a backout. In scenarios that cannot wait, we have a team of approvers that can provide off hours support.
* [Click here](https://confluence.sys.cigna.com/display/CLOUD/Cloud+CoE+AWS+Engineering+On+Call+Support) for instructions on how to page out off hours support.

