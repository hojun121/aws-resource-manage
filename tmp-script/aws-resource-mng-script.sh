# hoya aws credentials
export AWS_ACCESS_KEY_ID=AKIAVHB7HIAT7ERYSSFN
export AWS_SECRET_ACCESS_KEY=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
export AWS_REGION=ap-northeast-2
docker build -t steampipe-dashboard .
docker run --name steampipe-dashboard -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_REGION=$AWS_REGION -p9194:9194 -p9193:9193 -itd steampipe-dashboard
docker run -d -p 3000:3000 --name metabase metabase/metabase
