# CloudFormation

CloudFormationにて作成するリソースは以下の通り
* terraform state管理用S3
* terraform lock管理用DynamoDB
* terraformを実行するためのIAM user

```sh
$ aws cloudformation create-stack --stack-name okta-slackbot-test --template-body file://cfn.yaml --capabilities CAPABILITY_NAMED_IAM

$ aws cloudformation update-stack --stack-name okta-slackbot-test --template-body file://cloudformation/cfn.yaml --capabilities CAPABILITY_NAMED_IAM
```





## CICD雑めも
### 案１（terraformによる更新を諦める）
* テスト環境はローカルで
* mainマージ（tag打ちでも良い）
* appリポジトリを見て、変更がある場合は、container buildして、tagつける
* ecrにtagつけたやつをpush
* pushに成功したら、lambdaの更新をかける。これは、shellで`aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --image-uri $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG`な感じで更新してみる

### 案２（割と独自でいろいろやる）
* テスト環境はローカルで
* ecr.env的なファイルを用意しておいて、それでリリースバージョンを管理する
* mainマージ
* appリポジトリを見て、変更がある場合は、build
* tagをつける際は、ecr.envからタグを抜く
* tagをつけて、pushする
* pushに成功したら、lambdaの更新を書ける。この際に、terraform apply --variable ${ecr.env/TAG}みたいな形で、tagを上書きしてやる。

### 案３（インフラとアプリが1:1に対応させる。latestにて管理する）
* アプリをbuildしたら、latestタグにて、インフラをそのままデプロイする。
* ImageTagがそのままで、変更検知して、lambdaが更新されるかわからない
* latestタグだと無理そう（https://stackoverflow.com/questions/75265636/terraform-unable-to-update-lambda-with-ecr-image-on-new-image-publish）
* shellでpublishすればできそう。その場合は、１つ前に戻るのは多分厳しいから、切り戻し的なことはできずに、最新にどんどん入れ替えていくみたいなニュアンスになる。

### 案２の派生（コレがよさそう）
* トリガーはmainにtagが打たれた時でよさそう。
* ファイルを用意せずに、terraform実行時に、varを上書きする。
* インフラリソース上だと、何を最新化しているかわからんくなるので、appコードの変更に応じて、terraformが更新されていることを保証する

### pipelineとして２つ分けた方がいい（これはif分岐でよさそう）
* app変更に応じたterraform変更
* terraform変更に応じたterraform変更


### 守った方が良さそうなこと
* gitops。追跡できること
* 切り戻しができること
* バージョンと資材が1:1対応であること
* コンテナデプロイに対して、infraデプロイが連動すること

### 結論
* stg
    * トリガー
        * mainへのマージ
    * パイプライン（コンテナ更新時）
        * ecr.envというファイルを用意し、コンテナバージョンを管理する
        * コンテナに変更を加える際は、併せてecr.envも更新する。
        * コンテナへの変更を検知した場合は、buildする。
        * image tagがあるかチェックする。
        * pushする際は、上記のコンテナバージョンでpushする
        * push後、terraform apply --variable ${ecr.env/TAG}で、lambdaのimage verを上書きする
    * パイプライン（インフラ更新時）
        * コンテナへの変更を検知していないはずなので、スルー
        * terraform apply --variable ${ecr.env/TAG}　この場合、lambdaは変更されないので、上書きされない。
* prd
    * トリガー
        * tagをつける
    * パイプラインは上記と変わらない。

## Todo
* lambdaのsession managerから読めるようにする