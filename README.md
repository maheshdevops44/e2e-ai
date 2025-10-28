# Project title

One Paragraph of project description goes here.  Describe what the project does and why it is useful.

## Support disclaimer ⚠️

- Usage of aws-template does **not** come with any official support
- The goal of this repo is to give a easy and effective starting point for using GitHub actions and Terraform AWS deployments
- Ownership and maintenance is the responsibility of the app teams once the template is used

## Cloud architecture ☁️

Before development begins on the AWS workload, the team must design the cloud architecture.  See [these instructions](https://confluence.sys.cigna.com/display/CLOUD/P2P%3A+Start+With+a+Public+Cloud+Intake#P2P:StartWithaPublicCloudIntake-2:Createaclouddiagram%E2%98%81%EF%B8%8F) on how to create this in a public Confluence page with Draw.io.  See a starter cloud diagram a team can use to start out that includes everything this template repo creates by default:

![alt text](.github/assets/readme-4.png)

You can duplicate this diagram by viewing the original on Confluence [here](https://confluence.sys.cigna.com/display/CLOUD/Development%3A+GitHub+Cloud+Repo#expand-WhyusetheawstemplateformynewrepoHowdoIuseit). It is critical to provide a cloud architecture **before** beginning the [path 2 production](https://confluence.sys.cigna.com/pages/viewpage.action?pageId=779644424) to get a given workload deployed to a production AWS account.  

## AWS template overview 🛠 

This repository contains a generic reusable template for a Cigna AWS workload.  It implements boilerplate infrastructure as code files for AWS workloads written in [Terraform](https://developer.hashicorp.com/terraform).  

Read more about how to use this template when creating a new GitHub Cloud repo [here](https://confluence.sys.cigna.com/display/CLOUD/Development%3A+GitHub+Cloud+Repos).

### Core files 

See the following breakdown of the each of the core files within this template:
- `.github/`
    - `workflows/`
        - `aws-terraform-apply.yml` - A reusable workflow that is leveraged by GitHub actions workflows implemented per environment in the three following files described below.
        - `dev.yml` - A workflow for GitHub actions that will automatically run a terraform apply command to deploy the Terraform workload to a given dev AWS account when changes are pushed to any feature branch 
        - `test.yml` - Same as dev.yml except will deploy to the given test AWS account when changes are pushed to the `main` branch
        - `prod.yml` - Same as dev.yml except will deploy to the given prod AWS account when changes are pushed to the `release` branch
- `terraform/`
    - `base/` - Why put all our Terraform and state backends into this folder?  Teams are typically fine to use a single Terraform state file per environment, however as the project grows there are limitations depending on the team size and architecture pattern (ex: microservices).  By placing this workload in a module folder, this pattern can optionally be expanded by teams who down the road determine they need to split up Terraform state files.  Understand further [why a team would want to do this here](https://www.youtube.com/watch?v=wgzgVm7Sqlk).
        - `backends/`
            - `dev.tfvars` - This template enforces the use of [S3 backends](https://developer.hashicorp.com/terraform/language/backend/s3) for your Terraform state.  Understand why this is critical when teams work on the same Terraform states as described [here](https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/backend.html).  This file contains values that configure the [auto-created Terraform state S3 bucket](https://confluence.sys.cigna.com/display/CLOUD/2020.06.04+Standardized+Terraform+State+Backend+Resources) in the workloads AWS account as your S3 backend to save a given environments [Terraform state file](https://developer.hashicorp.com/terraform/language/state).  There are three of these because workloads will have to be deployed three times for the dev, test, and prod environments.  
            - `test.tfvars` - Same purpose but for the test AWS account
            - `prod.tfvars` - Same purpose but for the prod AWS account
            - NOTE that all these files need updated to include the respective AWS account ID and correct project name 
        - `environments/`
            - `dev.tfvars` - Contains the values for [Terraform variables](https://developer.hashicorp.com/terraform/language/values/variables) that change environment by environment.  For example imagine you want to create an [aws_lambda_function](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) and in dev the [memory_size](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function#memory_size-1) should be 128MB but in prod this should be 512MB.  You could create a variable named `lambda_memory_size` and set it to `128` in dev.tfvars and `512` in prod.tfvars.
            - `test.tfvars` - Same purpose but for the test AWS account
            - `prod.tfvars` - Same purpose but for the prod AWS account
        - `data.tf` - Contains all the [Terraform data sources](https://developer.hashicorp.com/terraform/language/data-sources) which import existing Terraform resources deployed by the Cloud CoE within a given AWS account.  Look through these data sources or the [Cigna documentation](https://confluence.sys.cigna.com/pages/viewpage.action?pageId=779644433#Hermes:AccountCreation&Access-5.WhatiscreatedautomaticallyinanewAWSaccount?%F0%9F%95%B5%F0%9F%8F%BE%E2%98%81%EF%B8%8F) to understand what existing infra can be leveraged in your workload.
        - `kms.tf` - Contains a customer managed KMS key that can be used for any data resources created in this workload.  It has a resource policy that has a modified version of the [default key policy statement](https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-default.html) in order to protect data.  This is a requirement for confidential and highly confidential data once a workloads [data classfification is determined](https://iris.cigna.com/business_units/cigna_technology_services_teams/information_protection/data_classification).
        - `providers.tf` - Contains all of the providers used in this workload, which includes the starter provider of `aws`.  Read more about [what a provider is here](https://developer.hashicorp.com/terraform/language/providers).
        - `variables.tf` - The concept of [variables](https://developer.hashicorp.com/terraform/language/values/variables) in Terraform allow you to reuse and customize a given module.  This is useful in this repository template as you can have different configurations for each environment the workload is deployed to (dev, test, and production).  This file is split into two sections -- one that includes variables that do not change between environments that leverage [default values](https://developer.hashicorp.com/terraform/language/values/variables#default-values) to keep your IaC DRY.  The other section is for variables that should change between environments (ex: VPC CIDR range) which has values assigned in the `environments/*.tfvars` files discussed earlier.
        - `vpc.tf` - Implements the [AWS VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html) resource using the [golden VPC module](https://github.sys.cigna.com/cigna/AWS-GoldenVPC) which has been customized to easily connect an AWS workload to on-prem resources / AWS VPC based compute to the Internet
- `README.md` - The document you are reading now.  Should be modified by the solution team to include details specific to this workload to improve onboarding and maintainability of the repo.

Why are we using a single module?  This template is designed to optimize for beginners.  So instead of forcing teams into a multiple module and Terraform state design this template keeps things as simple as possible.  For workloads supported by larger teams or as a workload grows, it may make sense to use [multiple Terraform state files](https://spacelift.io/blog/terraform-state#isolating-and-organizing-state-files) split across multiple modules that communicate via outputs.  

### Getting started 🚀

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The following are required installs to run a Terraform deployment manually:

```bash
# In order to authenticate in AWS, you will need to install saml2aws and get global groups for a given account.  See the full docs on how to do this below:
# https://confluence.sys.cigna.com/pages/viewpage.action?pageId=779644433#Hermes:AccountCreation&Access-3:RequestaccesstoanewAWSaccountinAveska%F0%9F%94%90

saml2aws login # Choose the correct role (typically ACCOUNTADMIN in dev accounts) to get CLI credentials that Terraform can use

# You will further need to install Terraform.  See instructions for your OS at the following link:
# https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli

terraform --version # Verifies that Terraform is installed
```

### Installing

The following outlined the required steps to perform your first manual Terraform deployment in dev:

1. Complete the `TODO` items listed in `backends/dev.tfvars`
    - In this file, we must specify the AWS account IDs we want to deploy for Terraform
    - For example, for an account ID of `108755756871` you would replace the value for `bucket = cigna-tf-state-108755756871`

2. Initialize the Terraform workload

```bash
# Terraform as an infrastructure as code (IaC) language must store the current state of the AWS resources in a Terraform state file
# Initializing the Terraform ensures that you have configured an S3 backend correctly, and installs any golden modules references along with providers required (as outlined in providers.tf)
# In the below command, we went to deploy to the dev AWS account so we must reference we want to use the dev backend file
terraform init --backend-config backends/dev.tfvars
```

![alt text](.github/assets/readme-1.png)

3. Deploy the Terraform

```bash
# Deploys the Terraform with the "apply" command which will compare the current Terraform state with the resources you specify in `.tf` files (ex: vpc.tf) and determine what needs deployed or updated
# This workload also outlines Terraform variables which have values that change in each environment (see the specific vars at environments/dev.tfvars)
# The --var-file flag tells our Terraform which values we would like to assign to these variables
terraform apply --var-file environments/dev.tfvars
```

This command should then prompt if you would like to apply the changes.  All the resources provisioned show the power of golden modules we are using, as we don't have to understand (although it is valuable to understand networking in AWS) everything it is doing.  The module will simply provide us a VPC which we can use and configure depending on our networking requirements.  Type `yes` into the terminal and hit the `Enter` key:

![alt text](.github/assets/readme-2.png)

4. Begin your AWS journey!
    - The next steps in your AWS development journey with Terraform are up to you! 
    - Discuss internally to understand the requirements of your workload, and put together a cloud architecture to plan all the AWS services required for a workload
        - See docs on how to do this [here](https://confluence.sys.cigna.com/display/CLOUD/P2P%3A+Start+With+a+Public+Cloud+Intake#P2P:StartWithaPublicCloudIntake-2:Createaclouddiagram%E2%98%81%EF%B8%8F)
        - Review proven patterns used across the enterprise at [golden brick road](https://gbr.cignacloud.com/)
    - If this architecture includes an SQS queue, you may want to make a file named `sqs.tf` and add a [aws_sqs_queue](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sqs_queue) resource to this and repeat step 3 above
    - There are additional files in this repo that must be completed in order to deploy to higher environments.  Check all of these out by performing a repo search in [VS Code](https://code.visualstudio.com/) for the term `TODO`:
        - ![alt text](.github/assets/readme-3.png)

### This stuff is cool but I'm lost 😵‍💫 how can I learn and get help?

You have found one of the [most common issues with teams starting in AWS](https://youtu.be/fnY0oLchK1Y?si=-T2SYtzChk2moWIl&t=421)!  Cigna provides an opportunity to learn these skills for full-time employees to get a license to use [Pluralsight](https://iris.cigna.com/business_units/cigna_technology/technologylearning/technical_skills/pluralsight).  See some recommended courses to checkout to help enable your understand of AWS concepts and Terraform:

- AWS basics: [AWS Certified Cloud Practitioner](https://app.pluralsight.com/paths/certificate/aws-certified-cloud-practitioner-clf-c02)
- Terraform basics: [Terraform - Getting Started](https://app.pluralsight.com/library/courses/terraform-getting-started-2023/table-of-contents)

Learning while doing is an advantage, pair progress on your new AWS workload with upskilling from these courses.

### Naming conventions

This is a crucial item to get awareness and coordination on during the early stages of a given AWS workload.  By following a standard naming convention, it will be significantly easier for developers, reviewers, prod support, and stakeholders to find and identify a given AWS workload.  This is ulitmately decided by a team, but see a recommended naming convention to help get you started:

`<project name>-<environment>-<primary purpose>`

For example, see the following example used for the KMS key with the purpose of a general customer managed key (cmk) created in this template:

`my-project-name-dev-cmk`

### CICD with GitHub Actions

For an in-depth explanation of how [GitHub Actions](https://pages.github.sys.cigna.com/cigna/github-cloud-documentation/docs/kb/actions.html#github-actions) is used within this template repository, you can check out the following documentation at the respective page in the Cloud CoE P2P complete guide:

[DevOps: CICD with GitHub Actions](https://confluence.sys.cigna.com/display/CLOUD/DevOps%3A+CICD+with+GitHub+Actions)

Note that all the related files are located in the `.github/workflows` folder and you can view how the default workflows perform Terraform deployments at the [example aws-hello-world repo](https://github.com/cigna-group/aws-hello-world/actions).  This repo uses this aws-template as a template, and shows what updated usage of the repo looks like.  

### Golden Shared Workflows 

You can further integrate your workloads CICD with shared Cigna workflows located at the [golden-shared-workflows](https://github.com/cigna-group/golden-shared-workflows/tree/main) repository.    

### Ideas 💡

- Add a container build process
- Add an example Lambda code and deployment in the repo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Code Owners

Please read [CODEOWNERS](.github/CODEOWNERS) for details on the code owners of our repo

## License

Describe any CIGNA license info

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc


## Steps
```bash
terraform init --backend-config backends/dev.tfvars
```
```bash
terraform apply --var-file environments/dev.tfvars
```
