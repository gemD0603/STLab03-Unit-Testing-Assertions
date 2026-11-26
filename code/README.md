# STLab03 – Unit Testing & Assertions (EduParking)

Bài làm môn Software Testing: kiểm thử đơn vị ứng dụng bãi giữ xe **EduParking** bằng `pytest`
(Requirement → Unit Test → Test Report → Defect → Regression → Mutant).

- Sinh viên: `21110275_MaiNguyenNgocDuy`
- Hạn nộp: 08/12/2026

## Cấu trúc

| Tệp / thư mục | Nội dung |
|---|---|
| `parking_app.py` | Ứng dụng EduParking **v2 (đã sửa 4 lỗi)** – bản trong repo; chạy notebook sẽ ghi lại v1 rồi sửa thành v2 |
| `parking_app_v1.py` | Bản v1 gốc (chưa sửa) giữ làm bằng chứng lỗi |
| `test_functions.py` | Test REQ-01 → REQ-05 (hàm thuần) |
| `test_parking_lot.py` | Test REQ-06 → REQ-12 (lớp `ParkingLot`, có `setup_method`) |
| `test_report.py` | Chạy pytest và xuất Test Report (XML, CSV, Excel, HTML, biểu đồ) |
| `test_problem_solving.py` | Minh chứng Phần 3.3 |
| `demo_interview.py`, `demo_coverage.py` | Demo code interview A–D và coverage cao nhưng test yếu (không nằm trong report chính) |
| `reports/v1`, `reports/v2` | Test Report lần 1 (trước khi sửa) và lần 2 (sau khi sửa) |
| `MSSV_HoTenSinhVien_STLab03.ipynb` | Notebook chạy từ đầu đến cuối |

## Chạy

Google Colab: mở notebook, **Runtime ▸ Run all**.

Máy cục bộ:

```bash
pip install -r requirements.txt
python -m pytest test_functions.py test_parking_lot.py -v
```

Nếu muốn tái tạo v1/v2 và report, chạy notebook (cell ghi `parking_app.py` v1, build report v1, sửa lỗi, build report v2).

## Kết quả mong đợi

| | Test | PASS | FAIL | Ghi chú |
|---|---|---|---|---|
| v1 | 81 | 74 | 7 | 4 defect (REQ-02, 06, 09, 12) |
| v2 | 81 | 81 | 0 | line ≥ 95%, branch ≥ 90% |

Mutant trên v2: 10 mutant, 9 bị giết, 1 tương đương (`hours < 1` → `hours <= 0`).

## Nguyên tắc

Expected suy ra từ requirement, không sửa expected để khớp ứng dụng; không dùng mock/fixture (thuộc Bài 7).
