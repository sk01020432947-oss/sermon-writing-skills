#!/bin/bash
# 모든 샘플을 고품질(1080p·모션블러)로 렌더. 사용: bash render_hq_all.sh [동시 작업 수=4] [폴더 패턴...]
J=${1:-4}; shift
cd "$(dirname "$0")/../samples"
LIST=${@:-$(ls -d [0-9][0-9]-*/)}
printf '%s\n' $LIST | xargs -P "$J" -I{} sh -c 'node ../scripts/render_hq.mjs "{}" 2>&1 | tail -1'
