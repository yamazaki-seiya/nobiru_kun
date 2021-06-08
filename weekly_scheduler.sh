#!/bin/bash
# 月曜日(1)に限り、このスクリプトを実行すると、パイプラインで指定したコマンドが実行される。
CMDNAME=$1
if [ "$(date +%u)" = 1 ]; then $CMDNAME; fi
