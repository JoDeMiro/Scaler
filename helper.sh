#!/bin/bash

# Set up a default search path
PATH="/usr/bin:/bin"

CURL=`which curl`
if [ -z "$CURL" ]; then
  echo "curl not found"
  exit 1
fi

target="http://127.0.0.1/balancer-manager"
host="127.0.0.1"
while getopts "t:h:" opt; do
  case "$opt" in
    t)
      target=$OPTARG
      ;;
    h)
      host=$OPTARG
      ;;
  esac
done

curlopts="--insecure§-H§Host: $host§-H§Referer: http://$host/balancer-manager"

shift $(($OPTIND - 1))
action=$1


list_balancers() {
  OFS=$IFS
  IFS="§"
  $CURL $curlopts -s "${target}" | grep "balancer://" | sed "s/.*balancer:\/\/\(.*\)<\/a>.*/\1/"
  IFS=$OFS
}

list_workers() {
  balancer=$1
  if [ -z "$balancer" ]; then
    echo "Usage: $0 [-s host] [-p port] [-m balancer-manager]  list-workers  balancer_name"
    echo "  balancer_name :    balancer name"
    exit 1
  fi

  OFS=$IFS
  IFS="§"
  OUT=$($CURL $curlopts -s "${target}")
  IFS=$OFS

  echo "${OUT}" | grep "/balancer-manager?b=${balancer}&amp;w" | sed "s/.*href='\(.[^']*\).*/\1/" | sed "s/.*w=\(.*\)&.*/\1/"
}

enable() {
  balancer=$1
  worker=$2
  if [ -z "$balancer" ] || [ -z "$worker" ]; then
    echo "Usage: $0 [-s host] [-p port] [-m balancer-manager]  enable  balancer_name  worker_route"
    echo "  balancer_name :    balancer/cluster name"
    echo "  worker_route  :    worker route e.g.) ajp://192.1.2.3:8009"
    exit 1
  fi

  OFS=$IFS
  IFS="§"

  nonce=`$CURL $curlopts -s "${target}" | grep nonce | grep "${balancer}" | sed "s/.*nonce=\(.*\)['\"].*/\1/" | tail -n 1`
  if [ -z "$nonce" ]; then
    echo "balancer_name ($balancer) not found"
    exit 1
  fi

  echo "Enabling $2 of $1..."
  # Apache 2.2.x
  #$CURL $curlopts -s -o /dev/null "${target}?b=${balancer}&w=${worker}&nonce=${nonce}&dw=Enable&lf=1&ls=0&wr=&rr="

  # newer Apache
  $CURL $curlopts -s -o /dev/null -XPOST "${target}?" -d b="${balancer}" -d w="${worker}" -d nonce="${nonce}" -d w_status_D=0

  IFS=$OFS

  sleep 0.5
  status
}

disable() {
  balancer=$1
  worker=$2
  if [ -z "$balancer" ] || [ -z "$worker" ]; then
    echo "Usage: $0 [-s host] [-p port] [-m balancer-manager]  disable  balancer_name  worker_route"
    echo "  balancer_name :    balancer/cluster name"
    echo "  worker_route  :    worker route e.g.) ajp://192.1.2.3:8009"
    exit 1
  fi

  OFS=$IFS
  IFS="§"

  echo "Disabling $2 of $1..."
  nonce=`$CURL $curlopts -s "${target}" | grep nonce | grep "${balancer}" | sed "s/.*nonce=\(.*\)['\"].*/\1/" | tail -n 1`
  if [ -z "$nonce" ]; then
    echo "balancer_name ($balancer) not found"
    exit 1
  fi

  # Apache 2.2.x
  #$CURL $curlopts -s -o /dev/null "${target}?b=${balancer}&w=${worker}&nonce=${nonce}&dw=Disable&lf=1&ls=0&wr=&rr="

  # Newer Apache ...
  $CURL $curlopts -s -o /dev/null -XPOST "${target}" -d b="${balancer}" -d w="${worker}" -d nonce="${nonce}" -d w_status_D=1

  IFS=$OFS

  sleep 0.5
  status
}

status() {
  OFS=$IFS
  IFS="§"

  $CURL $curlopts -s "${target}" | grep "href" | sed "s/<[^>]*>/ /g"

  IFS=$OFS
}

case "$1" in
  list-balancer)
    list_balancers "${@:2}"
        ;;
  list-worker)
    list_workers "${@:2}"
        ;;
  enable)
    enable "${@:2}"
        ;;
  disable)
    disable "${@:2}"
        ;;
  status)
    status "${@:2}"
        ;;
  *)
    echo "Usage: $0 {list-balancer|list-worker|enable|disable|status}"
        echo ""
        echo "Options: "
        echo "    -t target (e.g. https://app.acme.com/balancer-manager)"
        echo ""
        echo "Commands: "
        echo "    list-balancer"
        echo "    list-worker  balancer-name"
        echo "    enable   balancer_name  worker_route"
        echo "    disable  balancer_name  worker_route"
    exit 1
esac

exit $?