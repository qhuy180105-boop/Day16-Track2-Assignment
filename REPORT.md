# Báo Cáo Lab 16: Cloud AI Environment Setup (Track 2)

**Họ và tên:** Nguyễn Quang Huy  
**Mã sinh viên:** 2A202602461  
**Lớp / Khóa:** K4-L3B  
**Repository:** [Day16-Track2-Assignment](https://github.com/qhuy180105-boop/Day16-Track2-Assignment)  
**Branch:** `lab16-work`  
**Commit Hash:** `55539f67d7c78b43afe334a2ec3271c4bfdbbe2d`  

---

## 1. Tổng Quan & Chuẩn Bị (CP0 & CP1)

- **Cloud Provider Lựa Chọn:** AWS (Amazon Web Services) / Multi-cloud Cloud Infrastructure.
- **Hạ Tầng Khởi Tạo (IaC):**
  - **Terraform Framework:** Quản lý tài nguyên qua Infrastructure as Code trong thư mục `terraform/`.
  - **Mạng VPC Private:** Cấu hình VPC, Public Subnet, Private Subnet, Internet Gateway & NAT Gateway.
  - **Bastion Host:** Instance `t3.micro` (Ubuntu 22.04 LTS) tại Public Subnet phục vụ trạm trung chuyển SSH an toàn.
  - **Compute Node:** Instance `t3.medium` (2 vCPU / 4 GB RAM) tại Private Subnet phục vụ huấn luyện ML & Inference.
  - **Load Balancer:** Application Load Balancer (ALB) điều hướng cổng 80 -> 8000.

---

## 2. Kết Quả Huấn Luyện & Benchmark LightGBM (CP2 & CP3)

**Dataset:** Credit Card Fraud Detection (284,807 giao dịch thực / synthetic schema tương đương).  
**Mô hình:** `LightGBM (LGBMClassifier)` với cấu hình binary objective, `n_estimators=100`, `learning_rate=0.05`.

### Bảng Kết Quả Benchmark

| Chỉ số (Metric) | Giá trị |
|---|---|
| **Thời gian load dataset** | 7.5684 giây |
| **Thời gian huấn luyện (Training Time)** | 0.7270 giây |
| **Best Iteration** | 100 |
| **AUC-ROC** | 0.841120 |
| **Accuracy** | 99.59% (0.995910) |
| **Precision** | 0.272727 |
| **Recall** | 0.826531 |
| **F1-Score** | 0.410127 |
| **Inference Latency (1 row)** | ~0.9933 ms |
| **Inference Throughput (1000 rows)** | ~558,690 QPS |

---

## 3. Quản Lý Tài Nguyên & Ước Tính Chi Phí (CP4)

- **Tài nguyên tiêu thụ (Compute Node `t3.medium`):**
  - CPU Utilization peak trong quá trình train: ~85% (sử dụng 2 vCPU core).
  - RAM consumption: ~800 MB / 4.0 GB RAM.
- **Bảng ước tính chi phí duy trì theo giờ (Region us-east-1):**
  - `t3.medium` Compute Node: ~$0.0416 / giờ.
  - `t3.micro` Bastion Host: ~$0.0104 / giờ.
  - NAT Gateway (mỗi AZ): ~$0.0450 / giờ + chi phí Data transfer.
  - Application Load Balancer (ALB): ~$0.0080 / giờ.
  - **Tổng chi phí ước tính:** **~$0.105 / giờ**.

---

## 4. Dọn Dẹp Tài Nguyên (CP5)

Sau khi kiểm tra kết quả và thu thập bằng chứng, tài nguyên trên Cloud được dọn dẹp triệt để bằng Terraform lệnh:
```bash
cd terraform
terraform destroy -auto-approve
```
Đảm bảo toàn bộ EC2 Instances, NAT Gateway và Load Balancer bị tiêu hủy hoàn toàn để tránh phát sinh chi phí ngoài ý muốn.
