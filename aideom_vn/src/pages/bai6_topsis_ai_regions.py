import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from m2_readiness import topsis, entropy_weights
except ImportError:
    def topsis(*args): return np.zeros(6), np.arange(6)+1
    def entropy_weights(*args): return np.array([1/8]*8)

def render():
    st.title("🏆 Bài 6 — TOPSIS: Xếp hạng mức độ ưu tiên đầu tư AI cho các địa phương")
    
    st.markdown("""
    **Mục tiêu học tập:** Sinh viên nắm vững phương pháp Ra quyết định đa tiêu chí (MCDM) TOPSIS. 
    Học cách xử lý các tiêu chí có hướng khác nhau (Benefit (+) và Cost (-)) và cách tính trọng số 
    khách quan bằng phương pháp Entropy.
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Vấn đề", 
        "🔬 Lý thuyết TOPSIS", 
        "🛠️ Thuật toán Entropy", 
        "📊 Dữ liệu 10 tỉnh trọng điểm", 
        "📈 Kết quả xếp hạng", 
        "💡 Phân tích chiến lược",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Theo Chiến lược quốc gia về AI (Quyết định 127/QĐ-TTg), Việt Nam cần xây dựng 3 trung tâm quốc gia 
        về lưu trữ dữ liệu lớn và tính toán hiệu năng cao. 
        
        **Vấn đề:** Trong số các tỉnh thành trọng điểm, địa phương nào hội tụ đủ các yếu tố để đặt các trung tâm này? 
        Cần một phương pháp đánh giá đa chiều bao gồm: Kinh tế, Hạ tầng số, Nhân lực và Chính sách.
        """)
        st.info("💡 **Phương pháp:** TOPSIS giúp tìm ra phương án có khoảng cách gần nhất với 'Lý tưởng dương' và xa nhất với 'Lý tưởng âm'.")
        
    with tabs[1]:
        st.header("2. Lý thuyết TOPSIS")
        st.markdown("TOPSIS (*Technique for Order of Preference by Similarity to Ideal Solution*)")
        
        st.markdown("**Các bước thực hiện:**")
        st.latex(r"r_{ij} = \frac{x_{ij}}{\sqrt{\sum x_{ij}^2}} \quad \text{(Chuẩn hóa Vector)}")
        st.latex(r"v_{ij} = w_j \cdot r_{ij} \quad \text{(Nhân trọng số)}")
        st.markdown("**Xác định giải pháp lý tưởng:**")
        st.markdown("- **Lý tưởng dương ($A^+$):** Tập hợp các giá trị tốt nhất của mỗi tiêu chí.")
        st.markdown("- **Lý tưởng âm ($A^-$):** Tập hợp các giá trị tệ nhất của mỗi tiêu chí.")
        st.latex(r"C_i = \frac{D_i^-}{D_i^+ + D_i^-}")
        st.caption(r"Trong đó $C_i \in [0, 1]$, càng gần 1 phương án càng tối ưu.")

    with tabs[2]:
        st.header("3. Phương pháp Trọng số Entropy")
        st.markdown("""
        Nếu không có ý kiến chuyên gia, ta dùng Entropy để đo lường độ 'phân kỳ' của dữ liệu. 
        Tiêu chí nào có dữ liệu càng biến động (entropy thấp) thì tiêu chí đó càng mang nhiều thông tin và trọng số cao hơn.
        """)
        st.latex(r"e_j = -k \sum p_{ij} \ln(p_{ij})")
        st.latex(r"w_j = \frac{1-e_j}{\sum (1-e_j)}")

    with tabs[3]:
        st.header("4. Dữ liệu 10 tỉnh thành/vùng tiêu biểu (2024)")
        data = {
            "Địa phương": ["Hà Nội", "TP. HCM", "Đà Nẵng", "Bắc Ninh", "Bình Dương", "Hải Phòng", "Cần Thơ", "Quảng Ninh", "Thái Nguyên", "Lâm Đồng"],
            "GRDP_Capita": [150, 165, 95, 145, 170, 135, 85, 140, 90, 75],
            "Digi_Index": [82, 85, 80, 75, 78, 76, 70, 77, 72, 65],
            "AI_Talent": [95, 98, 75, 60, 65, 55, 50, 45, 60, 30],
            "FDI_Project": [450, 600, 120, 180, 350, 220, 80, 150, 95, 40],
            "IT_Park": [5, 4, 3, 2, 2, 1, 1, 1, 1, 0],
            "Cost_Index": [85, 90, 65, 75, 80, 78, 60, 72, 62, 55] # Tiêu chí COST (-)
        }
        df_t = pd.DataFrame(data)
        st.table(df_t)
        st.caption("Dữ liệu mô phỏng dựa trên chỉ số DTI và PCI 2024.")

    with tabs[4]:
        st.header("5. Kết quả xếp hạng")
        
        # Criteria directions
        is_benefit = [True, True, True, True, True, False] # Cost_Index is cost
        cols = ["GRDP_Capita", "Digi_Index", "AI_Talent", "FDI_Project", "IT_Park", "Cost_Index"]
        
        # User weights or Entropy
        w_mode = st.radio("Chọn phương diện trọng số:", ["Đồng đều", "Ưu tiên Công nghệ (Digital/AI)", "Tự động (Entropy)"])
        
        X = df_t[cols].values.astype(float)
        if w_mode == "Đồng đều":
            w = np.array([1/6]*6)
        elif w_mode == "Ưu tiên Công nghệ (Digital/AI)":
            w = np.array([0.1, 0.3, 0.3, 0.1, 0.1, 0.1])
        else:
            # Simple entropy
            P = X / X.sum(axis=0)
            E = - (P * np.log(P + 1e-9)).sum(axis=0) / np.log(len(df_t))
            w = (1 - E) / (1 - E).sum()
            
        # TOPSIS Solver
        # 1. Normalization
        norm_X = X / np.sqrt((X**2).sum(axis=0))
        # 2. Weighted Matrix
        V = norm_X * w
        # 3. PIS and NIS
        pis = np.zeros(6)
        nis = np.zeros(6)
        for j in range(6):
            if is_benefit[j]:
                pis[j] = V[:, j].max()
                nis[j] = V[:, j].min()
            else:
                pis[j] = V[:, j].min()
                nis[j] = V[:, j].max()
        # 4. Distances
        d_plus = np.sqrt(((V - pis)**2).sum(axis=1))
        d_minus = np.sqrt(((V - nis)**2).sum(axis=1))
        # 5. Closeness
        scores = d_minus / (d_plus + d_minus)
        
        df_t['TOPSIS_Score'] = scores
        df_t['Rank'] = df_t['TOPSIS_Score'].rank(ascending=False).astype(int)
        df_res = df_t.sort_values('Rank')
        
        st.write(f"Sử dụng bộ trọng số: `{np.round(w, 2).tolist()}`")
        
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.dataframe(df_res[['Rank', 'Địa phương', 'TOPSIS_Score']].style.format({'TOPSIS_Score': '{:.4f}'}))
        with col2:
            fig = px.scatter(df_res, x='Digi_Index', y='TOPSIS_Score', size='AI_Talent', color='Địa phương',
                             hover_name='Địa phương', title="Sự tương quan Digi Index và Điểm TOPSIS")
            st.plotly_chart(fig, use_container_width=True)

    with tabs[5]:
        st.header("6. Thảo luận chiến lược")
        st.markdown("""
        - **Cặp đôi dẫn đầu:** Hà Nội và TP.HCM luôn cạnh tranh vị trí số 1. Hà Nội mạnh về Nhân lực (AI Talent), TP.HCM mạnh về FDI và quy mô kinh tế.
        - **Hiện tượng Đà Nẵng:** Dù quy mô kinh tế (GRDP) nhỏ hơn Bình Dương, nhưng nhờ chỉ số Digital (Digi_Index) và hạ tầng (IT Park) tốt, Đà Nẵng vẫn xếp hạng cao.
        - **Ràng buộc Chi phí:** Các địa phương như Bình Dương có Cost_Index cao (đắt đỏ) làm giảm nhẹ điểm TOPSIS so với các nơi có chi phí vận hành rẻ hơn.
        - **Kết luận:** Hà Nội, TP.HCM và Đà Nẵng là 3 cái tên sáng giá nhất để hình thành các Hub AI quốc gia.
        """)
        
    with tabs[6]:
        st.header("Tham khảo")
        st.markdown("""
        - **Quyết định số 127/QĐ-TTg** về Chiến lược quốc gia về nghiên cứu, phát triển và ứng dụng AI.
        - **Hwang & Yoon:** Multiple Attribute Decision Making: Methods and Applications.
        - **Vietnam Regions Data 2024** (AIDEOM internal report).
        """)

if __name__ == "__main__":
    render()
