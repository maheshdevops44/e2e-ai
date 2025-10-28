bucket         = "cigna-tf-state-<my prod aws account id here>" # TODO: replace with your prod AWS account ID (if it exists)
key            = "base/my-project-name.tfstate" # TODO: replace with your AWS workloads project name
region         = "us-east-1"
dynamodb_table = "cigna-tf-lock-<my prod aws account id here>" # TODO: replace with your prod AWS account ID (if it exists)
encrypt        = true