server_dir=$1
country=$2
language=$3
port_1=$4
port_2=$5

mkdir -p ${server_dir}
pip install -r requirements.txt
apt-get install -y python-lucene
pip install awscli --ignore-installed six

aws_config="[default]\naws_access_key_id=AKIAIEGS6FVPJ2LA3HVA\naws_secret_access_key=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\nregion=us-west-1\noutput=json"

mkdir /root/.aws
printf ${aws_config} > /root/.aws/config

mkdir data
mkdir model_data

aws s3 sync s3://opera-images/nlp_service_data/supervised_keywords/data/${language} ./data/${language}
aws s3 sync s3://opera-images/nlp_service_data/supervised_keywords/model_data/${language} ./model_data/${language}
mkdir log


sed "s@<install_dir>@${server_dir}@" supervisor.tmp |  sed "s@<country>@${country}@" | sed "s@<language>@${language}@" | sed "s@<port_1>@${port_1}@" | sed "s@<port_2>@${port_2}@" > /etc/supervisor/conf.d/supervised_keywords_${country}.conf
cp -fr ./* ${server_dir}/
