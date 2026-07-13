import pandas as pd
import numpy as np

danh_sach_file = [
    "File_1.xlsx",
    "File_2.xlsx"
]

danh_sach_df = []

for file in danh_sach_file:
    try:
        df_tam = pd.read_excel(file)
        danh_sach_df.append(df_tam)
        print(f" Đã đọc thành công file: {file}")
    except Exception as e:
        print(f" Lỗi khi đọc file {file}: {e}")
df = pd.concat(danh_sach_df, ignore_index=True)

df_left = df[["Mã số mẫu", "Unnamed: 3", "DNAEXT"]].dropna(subset=["Mã số mẫu"])
df_right = df[["Mã số mẫu.1","Unnamed: 9" ,"DNAEXT.1"]].dropna(subset=["Mã số mẫu.1"])
df_right.columns =["Mã số mẫu","Unnamed: 3" ,"DNAEXT"]

df_clean = pd.concat([df_left, df_right], ignore_index= True)
df_clean["DNAEXT"] = pd.to_numeric(df_clean["DNAEXT"], errors="coerce")
df_clean = df_clean.dropna(subset=["DNAEXT"])
df_clean= df_clean.rename(columns={"Unnamed: 3": "Số lần tách"})
df_clean["Số lần tách"] = df_clean["Số lần tách"].fillna(1).astype(int)

df_ket_qua = df_clean[["Mã số mẫu", "Số lần tách", "DNAEXT"]]

# display(df_ket_qua)

df_grouped = df_ket_qua.groupby("Mã số mẫu").agg(Nồng_độ_trung_bình =("DNAEXT", "mean"), Danh_sách_nồng_độ =("DNAEXT", list), Danh_sách_lần_tách=("Số lần tách", list)).reset_index()
df_grouped['Tổng số lần tách'] = df_grouped['Danh_sách_lần_tách'].apply(len)

df_grouped['C1'] = df_grouped.apply(lambda x: x['Danh_sách_nồng_độ'][x['Danh_sách_lần_tách'].index(1)] if 1 in x['Danh_sách_lần_tách'] else 0, axis=1)
df_grouped['C2'] = df_grouped.apply(lambda x: x['Danh_sách_nồng_độ'][x["Danh_sách_lần_tách"].index(2)] if 2 in x['Danh_sách_lần_tách'] else 0, axis=1)
df_grouped['C3'] = df_grouped.apply(lambda x: x['Danh_sách_nồng_độ'][x["Danh_sách_lần_tách"].index(3)] if 3 in x['Danh_sách_lần_tách'] else 0, axis=1)
df_grouped['C4'] = df_grouped.apply(lambda x: x['Danh_sách_nồng_độ'][x["Danh_sách_lần_tách"].index(4)] if 4 in x['Danh_sách_lần_tách'] else 0, axis=1)

df_grouped["Thể tích"] = df_grouped["Tổng số lần tách"] * 40
df_grouped["Tổng lượng"] = df_grouped["Nồng_độ_trung_bình"] * df_grouped["Thể tích"]

# display(df_grouped)

def phan_loai_mau(row):
  v = row["Thể tích"]
  tong_luong = row["Tổng lượng"]
  c1 = row["C1"]
  c2 = row["C2"]
  c3 = row["C3"]
  c4 = row["C4"]
  lan_tach = row["Danh_sách_lần_tách"]

  if c1 > 0 and c2 > 0 and ((c1+c2)/2 >= 0.6):
    return "đưa lai"

  if tong_luong < 3:
    return "tách thêm (nếu còn), do lại quantus nếu <3 thu lại"

  if c1 > 0 and c2 > 0 and ((c1+c2)/2 < 0.6) and lan_tach == [1, 2] and v == 80:
    if 25 <= tong_luong < 48:
      return "a"
    elif 15 <= tong_luong < 25:
      return "b"
    elif tong_luong < 15:
      return "tách thêm, nếu hết là b"
    else:
      return "đưa lai"


  elif c1 > 0 and c2 > 0 and c3>0 and lan_tach == [1, 2, 3] and v == 120:
    if tong_luong >= 25:
      return "c + 40µl elute"
    else:
      return "d + 40µl elute"


  elif c1 > 0 and c2 > 0 and c3>0 and c4>0 and lan_tach == [1, 2, 3, 4] and v >= 160:
    if 25 <= tong_luong <= 50:
      return "c"
    elif tong_luong < 25:
        return "d"
    else:
        return tong_luong

  return "Ngoại lệ (Chưa có quy tắc)"

df_grouped['Note'] = df_grouped.apply(phan_loai_mau, axis=1)
display(df_grouped)

ten_file_xuat = "Ket_qua_phan_loai_mau.xlsx"
df_grouped.to_excel(ten_file_xuat, index=False)
print(f"Đã lưu thành công file: {ten_file_xuat}")
