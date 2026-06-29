#!/bin/bash

main(){
  local do_migrate=true
  while true; do
    case "$1" in
      ##    0.........1.........2.........3.........4.........5.........6.........7.........8
      ###0: [OPTIONS...] manage.py ...
      ###0: [OPTIONS...] server
      ###0: [OPTIONS...] worker
      ###0:
      ###0: OPTIONS:
      ###0:
      -h|--help) ###1: - Show Help
        show_options
        exit 1
        ;;
      --no-migrate)
        do_migrate=false
        shift
        ;;
      *)
        break
        ;;
    esac
  done

  mkdir -p "$CELUTZ_DATA_DIR/media"


  if $do_migrate; then
    ( set -x;
      ./manage.py migrate
    )
  fi

  case "$1" in
    manage.py)
      shift
      set -x
      exec ./manage.py "$@"
      ;;
    server)
      shift
      set -x
      exec ./manage.py runserver "$@"
      ;;
    worker)
      shift
      set -x
      exec celery -A celutz.celery worker -c 1 "$@"
      ;;
    *)
      shift
      set -x
      exec "$@"
      ;;
  esac
}


show_options(){
  sed -rn \
    -e 's/\s*(\S*)\)\s\s*###([0-9]*:)\s*-\s\s*(.*)/\2\t\1\n\2\t\t\3\n\2/p' \
    -e 's/.*\)\s\s*###([0-9]*:)\s*(.*)\s*\s--\s\s*(.*)/\1\t\2\n\1\t\t\3\n\1/p' \
    -e 's/.*\)\s\s*###([0-9]*:)\s*(\S*)\s\s*(.*)/\1\t\2\n\1\t\t\3\n\1/p' \
    -e 's/^\s*###([0-9]*:)\s?(\s*)\$0(\s.*)/\1\2'"$(basename "$0")"'\3/p' \
    -e 's/^\s*###([0-9]*:)\s?(.*)/\1\2/p' \
    "$self" \
  | grep -n '' \
  | sed -r 's/^([0-9]*):([0-9]*):/\2.\1:/' \
  | sort -t: -k 1V \
  | cut -d: -f2-
}

echo "main" "$@"
main "$@"
