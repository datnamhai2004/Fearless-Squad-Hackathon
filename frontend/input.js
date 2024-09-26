function fetchData() {
    // URL của API backend để lấy dữ liệu dự đoán (endpoint trả về JSON)
    const url = 'http://localhost:8000/input'; // Gọi đúng URL của API trả về JSON

    // Sử dụng Fetch API để gửi yêu cầu GET đến backend
    fetch(url)
        .then(response => {
            // Kiểm tra nếu response thành công
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // Chuyển đổi dữ liệu thành JSON
            return response.json();
        })
        .then(data => {
            // Hiển thị dữ liệu lên giao diện
            displayData(data);
        })
        .catch(error => {
            // Xử lý lỗi nếu có
            console.error('There was an error!', error);
        });
}

// Hàm hiển thị dữ liệu lên giao diện
function displayData(data) {
    // Lấy phần tử chứa kết quả có id là output
    const container = document.getElementById('output');

    // Hiển thị kết quả dự đoán lên giao diện
    container.innerHTML = `<p>Prediction: ${data.prediction}</p>`; // Hiển thị giá trị prediction
}

// Gọi hàm fetchData khi tải trang
window.onload = fetchData;