server_dir=$1
language=$2
port=$3

thrift -r --gen py keywords_v2.thrift
mkdir -p ${server_dir}

pip install awscli --ignore-installed six

aws_config="[default]\naws_access_key_id=AKIAIEGS6FVPJ2LA3HVA\naws_secret_access_key=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\nregion=us-west-1\noutput=json"

mkdir /root/.aws
printf ${aws_config} > /root/.aws/config

aws s3 ls /opera-images-sg/

pip install -r requirements.txt
python -m spacy download en_core_web_sm-2.0.0-alpha --direct

python nltk_download.py

aws s3 sync s3://opera-images/nlp_service_data/keywords_v2/${language}/data

sed  "s@<install_dir>@${server_dir}@" supervisor/keywords_v2 | sed  "s@<language>@${language}@" | sed  "s@<port>@${port}@" > /etc/supervisor/conf.d/keyword_v2_${language}.conf

mkdir log

cp -fr ./* ${server_dir}/