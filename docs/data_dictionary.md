# 📖 TỪ ĐIỂN DỮ LIỆU THÔ (RAW DATA DICTIONARY)

**Dự án**: CO4031 - Telecom Data Warehouse & DSS  
**Phiên bản**: 1.0 (Raw Layer)

---

## 1. Nguồn 1: `telecom_customer_churn.csv` (CRM & Subscriptions)

| Tên Cột | Kiểu Dữ Liệu | Giải thích Ý nghĩa Nghiệp vụ | Giá trị Mẫu |
| :--- | :--- | :--- | :--- |
| `customerID` | String (VARCHAR) | Mã định danh duy nhất của khách hàng (Natural Key) | `7590-VHVEG`, `5575-GNVDE` |
| `gender` | String | Giới tính của khách hàng | `Male`, `Female` |
| `SeniorCitizen` | Integer (0/1) | Khách hàng có phải người cao tuổi (>= 65 tuổi) | `0` (Không), `1` (Có) |
| `Partner` | String | Khách hàng có vợ/chồng hoặc người sống cùng | `Yes`, `No` |
| `Dependents` | String | Khách hàng có người phụ thuộc (con cái/người già) | `Yes`, `No` |
| `tenure` | Integer | Số tháng khách hàng đã gắn bó sử dụng dịch vụ | `1`, `34`, `72` |
| `PhoneService` | String | Khách hàng có đăng ký dịch vụ thoại cố định/di động | `Yes`, `No` |
| `MultipleLines` | String | Đăng ký nhiều đường truyền thoại | `Yes`, `No`, `No phone service` |
| `InternetService` | String | Loại công nghệ Internet kết nối | `DSL`, `Fiber optic`, `No` |
| `OnlineSecurity` | String | Gói bảo mật trực tuyến | `Yes`, `No`, `No internet service` |
| `OnlineBackup` | String | Dịch vụ sao lưu dữ liệu đám mây | `Yes`, `No`, `No internet service` |
| `DeviceProtection` | String | Gói bảo hiểm / bảo vệ thiết bị | `Yes`, `No`, `No internet service` |
| `TechSupport` | String | Gói dịch vụ hỗ trợ kỹ thuật ưu tiên | `Yes`, `No`, `No internet service` |
| `StreamingTV` | String | Dịch vụ truyền hình trực tuyến | `Yes`, `No`, `No internet service` |
| `StreamingMovies` | String | Dịch vụ xem phim trực tuyến | `Yes`, `No`, `No internet service` |
| `Contract` | String | Loại hợp đồng cam kết sử dụng | `Month-to-month`, `One year`, `Two year` |
| `PaperlessBilling`| String | Sử dụng hóa đơn điện tử không dùng giấy | `Yes`, `No` |
| `PaymentMethod` | String | Phương thức thanh toán cước hàng tháng | `Electronic check`, `Mailed check`, `Bank transfer (automatic)`, `Credit card (automatic)` |
| `MonthlyCharges` | Float | Số tiền cước phải trả định kỳ hàng tháng (USD) | `29.85`, `56.95`, `103.20` |
| `TotalCharges` | String/Float | Tổng số tiền cước tích lũy đã đóng (USD) | `29.85`, `1889.50` (có 11 ô rỗng `' '` khi `tenure=0`) |
| `Churn` | String | Trạng thái rời mạng trong tháng qua (**Biến mục tiêu ML**) | `Yes` (Rời mạng), `No` (Còn sử dụng) |

---

## 2. Nguồn 2: `telecom_customer_locations.csv` (Branch & Geolocation)

| Tên Cột | Kiểu Dữ Liệu | Giải thích Ý nghĩa Nghiệp vụ | Giá trị Mẫu |
| :--- | :--- | :--- | :--- |
| `customerID` | String | Mã khách hàng (Khóa ngoại liên kết Nguồn 1) | `7590-VHVEG` |
| `country` | String | Quốc gia | `United States` |
| `state` | String | Bang / Tiểu bang | `California` |
| `city` | String | Thành phố chi nhánh phục vụ | `Los Angeles`, `San Francisco`, `San Diego`, `San Jose`, `Sacramento`, v.v. |
| `zip_code` | String | Mã bưu chính khu vực | `90001`, `94102`, `92101`, v.v. |
| `region` | String | Phân vùng thị trường quản lý | `Southern California`, `Bay Area`, `Northern California`, `Central Valley` |
| `latitude` | Float | Tọa độ vĩ độ (phục vụ GIS & Heatmap trên Dashboard) | `33.973125` |
| `longitude` | Float | Tọa độ kinh độ (phục vụ GIS & Heatmap trên Dashboard) | `-118.247890` |
