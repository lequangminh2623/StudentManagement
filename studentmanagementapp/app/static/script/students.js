let isFetching = false;

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('fetch-students-btn')
        .addEventListener('click', function () {
            // Kiểm tra nếu đang fetch, không thực hiện hành động tiếp theo
            if (isFetching) return;

            isFetching = true;  // Đặt isFetching là true khi bắt đầu fetch
            console.log("Button clicked");

            fetchClassroomId()  // Gọi hàm để lấy classroom_id
                .then(classroomId => {
                    if (!classroomId) {
                        alert("Không tìm thấy classroom_id.");
                        return;
                    }

                    // Gửi yêu cầu lấy danh sách học sinh với classroomId vừa lấy được
                    fetch('/students_in_classroom', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({classroom_id: classroomId})
                    })
                        .then(response => response.json())
                        .then(data => {
                            console.log(data);
                            if (data.error) {
                                alert(data.error);
                                return;
                            }

                            // Hiển thị sĩ số lớp
                            document.getElementById('total-students').value = data.total_students;

                            const tableBody = document.getElementById('students-table-body');
                            tableBody.innerHTML = '';  // Clear the table before inserting new data

                            data.students.forEach(student => {
                                const row = document.createElement('tr');
                                row.setAttribute('data-student-id', student.id);
                                row.innerHTML = `
                                <td>${student.id}</td>
                                <td>${student.name}</td>
                                <td>${student.gender}</td>
                                <td>${student.phone}</td>
                                <td>${student.address}</td>
                                <td>${student.email}</td>
                                <td>${student.birthday}</td>
                                <td>${student.status}</td>
                                <td><button class="btn btn-danger delete-btn" data-student-id="${ student.id }">Xóa</button></td>
                            `;
                                tableBody.appendChild(row);
                            });
                        })
                        .catch(error => {
                            console.error('Error fetching students:', error);
                        })
                        .finally(() => {
                            isFetching = false;  // Đặt lại isFetching là false sau khi fetch xong
                        });
                })
                .catch(error => {
                    console.error('Error:', error);
                    isFetching = false;  // Đặt lại isFetching nếu xảy ra lỗi
                });
        });
});


function fetchClassroomId() {
    const schoolYearSelect = document.getElementById('school-year');
    const classroomSelect = document.getElementById('classroom');

    const schoolYearName = schoolYearSelect.options[schoolYearSelect.selectedIndex].value;
    const classroomName = classroomSelect.options[classroomSelect.selectedIndex].value;

    console.log('schoolYearName:', schoolYearName);
    console.log('classroomName:', classroomName);

    return fetch('/get_classroom_id', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            school_year_name: schoolYearName,
            classroom_name: classroomName
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                throw new Error(data.error);
            }
            return data.classroom_id;  // Trả về classroom_id
        })
        .catch(error => {
            console.error('Lỗi khi nạp classroom_id:', error);
            throw error;
        });
}

// Hàm xử lý sự kiện xóa trên document
document.addEventListener('click', function (event) {
    if (event.target && event.target.classList.contains('delete-btn')) {
        const studentId = event.target.dataset.studentId;

        if (!studentId) {
            alert("Không thể xác định ID học sinh để xóa.");
            return;
        }

        fetch('/delete_student', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);

                    const row = event.target.closest('tr');
                    row.remove();
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error deleting student:', error);
            });
    }
});