pipeline {
  agent any
  stages {
    stage('') {
      steps {
        sh 'LATEST_RELEASE=$(curl -Ls -o /dev/null -w %{url_effective} https://github.com/firefly-iii/firefly-iii/releases/latest | cut -d\'/\' -f8)'
      }
    }
  }
}