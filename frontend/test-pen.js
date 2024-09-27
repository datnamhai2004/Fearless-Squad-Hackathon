document.addEventListener('keydown', (event) => {
    // Kiểm tra nếu phím nhấn là chữ số (0-9)
    if (!isNaN(event.key) && event.key >= '0' && event.key <= '9') {
        // Lấy giá trị hiện tại từ các phần tử
        const currentValueElement = document.getElementById('current-value');
        const predictionValueElement = document.getElementById('prediction-value');

        // Lưu giá trị hiện tại vào lịch sử trước khi cập nhật
        const currentHistoryItem = document.createElement('li');
        currentHistoryItem.className = 'history-item';
        currentHistoryItem.textContent = ` ${currentValueElement.textContent.trim()}`;

        // Thêm vào đầu danh sách lịch sử
        const historyElement = document.getElementById('history-values');
        historyElement.prepend(currentHistoryItem);

        // Tạo giá trị mới dựa trên phím số
        const newValue = ` ${event.key}`;
        const newPrediction = ` ${event.key}`;

        // Cập nhật giá trị mới cho h1
        currentValueElement.textContent = newValue;

        // Sau 0.4 giây cập nhật giá trị prediction
        setTimeout(() => {
            predictionValueElement.textContent = newPrediction;
        }, 700);
    }
});