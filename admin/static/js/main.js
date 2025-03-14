$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
    
    // 初始化資料表格（如果存在）
    if ($.fn.DataTable && $('#ordersTable').length) {
        $('#ordersTable').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.10.24/i18n/Chinese-traditional.json"
            },
            "order": [[0, "desc"]]
        });
    }
});

// 自動關閉提示訊息
setTimeout(function() {
    $('.alert').fadeOut('slow');
}, 3000);
