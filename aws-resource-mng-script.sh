export AWS_ACCESS_KEY_ID=AKIAVHB7HIAT7ERYSSFN
export AWS_SECRET_ACCESS_KEY=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
export AWS_REGION=ap-northeast-2
docker build -t steampipe-dashboard --build-arg AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID --build-arg AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY --build-arg AWS_REGION=$AWS_REGION .
docker run --name steampipe-dashboard -p9194:9194 -p9193:9193 -itd steampipe-dashboard
#docker run -d -p 3000:3000 --name metabase metabase/metabase
