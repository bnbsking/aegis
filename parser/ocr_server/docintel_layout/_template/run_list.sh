set -x
set -e

FOLDER=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
MAX_RETRIES=3
TIMER_SECS=480

run_task() {
    local task_name="emc-adi-poc"
    
    # 1. 確保環境乾淨
    docker rm -f "$task_name" 2>/dev/null
    
    # 2. 執行任務 (背景)
    docker compose -f adi-docker-compose.yml run --rm \
        --name "$task_name" \
        emc-adi-poc \
        --pdf_path "/data/input/${base_filename}" \
        --output_path "/data/output/" &
    
    # 3. 輪詢檢查
    local elapsed=0
    local exit_code=1  # 預設失敗 (1)
    echo "開始監控任務輸出..."
    while [ $elapsed -lt $TIMER_SECS ]; do
        # 檢查檔案是否存在
        if ls output/*/*_analysis_result.json >/dev/null 2>&1; then
            echo "偵測到結果檔案, 任務提早完成。"
            exit_code=0  # 標記成功 (0)
            break
        fi
        # 每5秒檢查一次
        sleep 5
        elapsed=$((elapsed + 5))
    done

    # 4. 清理：如果超時或失敗，確保容器被殺掉
    docker rm -f "$task_name" 2>/dev/null
    if [ $exit_code -ne 0 ]; then
        echo "任務失敗或超時，已清理容器。"
    fi

    return $exit_code
}


cd $FOLDER


for file in input/*.pdf; do
    base_filename=$(basename "$file")
    echo "/data/input/${base_filename}"

    count=0
    while [ $count -le $MAX_RETRIES ]; do
        echo "執行任務 (嘗試次數: $((count + 1)))..."
        if run_task; then
            echo "任務執行成功。"
            break
        else
            count=$((count + 1))
            [ $count -le $MAX_RETRIES ] && echo "任務失敗，準備重試..." && sleep $((10 * count)) || echo "任務已達最大重試次數，宣告失敗。"
        fi
    done
done
