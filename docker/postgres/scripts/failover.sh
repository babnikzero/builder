#!/bin/bash -x
source $(dirname $0)/common
 FALLING_NODE=$1         # %d
 OLDPRIMARY_NODE=$2      # %P
 NEW_PRIMARY=$3          # %H
 PGDATA=$4               # %R

 if [ $FALLING_NODE = $OLDPRIMARY_NODE ]; then
      ssh -T $SSH_PARAMS postgres@$NEW_PRIMARY "touch $PGDATA/failover"
      #ssh -T $SSH_PARAMS postgres@$NEW_PRIMARY "rm -f $PGDATA/recovery.* $PGDATA/failover"
	echo "Ведущий сервер $FALLING_NODE  вышел из строя"
	echo "Новый ведущий сервер: $NEW_PRIMARY"
exit 0
fi;
	echo "Ведомый сервер $FALLING_NODE  вышел из строя"
 exit 0;
