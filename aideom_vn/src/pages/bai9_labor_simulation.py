import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import plotly.graph_objects as go

def render():
    st.title("👷 Bài 9 — Mô phỏng thị trường lao động dưới tác động của AI")
    
    st.markdown("""
    **Mục tiêu học tập:** Sử dụng ma trận dịch chuyển (Transition Matrix) để mô phỏng dòng lao động. 
    Sinh viên hiểu rõ cơ chế "Lao động sáng tạo ra việc làm" vs "Máy móc thay thế con người".
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Vấn đề", 
        "🔬 Lý thuyết Markov", 
        "🧠 Phân loại Kỹ năng", 
        "📊 Ma trận Dịch chuyển", 
        "📈 Mô phỏng dòng lao động (Sankey)", 
        "💡 Thảo luận chính sách",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Việt Nam có lợi thế dân số vàng với hơn 54 triệu lao động. Tuy nhiên, hơn 70% là lao động kỹ năng thấp 
        hoặc trung bình trong các ngành gia công, lắp ráp. 
        
        **Vấn đề:** Khi AI được triển khai diện rộng (Bài 5), các ngành như Dệt may, Da giày, Logistics (Bài 3) 
        sẽ chứng kiến sự sụt giảm nhu cầu lao động thủ công. Cần mô phỏng xem bao nhiêu phần trăm lao động 
        có thể chuyển đổi sang khu vực số hóa và bao nhiêu bị đào thải?
        """)
        
    with tabs[1]:
        st.header("2. Lý thuyết Chuỗi Markov")
        st.markdown(r"""
        Thị trường lao động được mô phỏng như một hệ thống chuyển dịch trạng thái. 
        Xác suất một công nhân chuyển từ ngành $i$ sang ngành $j$ được biểu diễn qua ma trận chuyển đổi $P$:
        """)
        st.latex(r"S_{t+1} = S_t \cdot P")
        st.markdown(r"""
        **Trong đó:**
        - $S_t$: Vector phân bố lao động tại thời điểm $t$.
        - $P$: Ma trận các xác suất chuyển dịch $p_{ij}$.
        - Tác động AI: Làm thay đổi các giá trị $p_{ij}$, đặc biệt là tăng xác suất chuyển dịch từ các ngành kỹ năng thấp sang thất nghiệp hoặc đào tạo lại.
        """)

    with tabs[2]:
        st.header("3. Phân loại 3 nhóm lao động chính")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("**Nhóm 1: Manual**")
            st.markdown("- Công việc lặp lại.\n- Rủi ro tự động hóa: **80%**.\n- Ví dụ: May mặc, lắp ráp.")
        with col2:
            st.warning("**Nhóm 2: Cognitive**")
            st.markdown("- Công việc văn phòng.\n- Rủi ro tự động hóa: **40%**.\n- Ví dụ: Kế toán, CSKH.")
        with col3:
            st.success("**Nhóm 3: AI-Hybrid**")
            st.markdown("- Sáng tạo & AI.\n- Rủi ro tự động hóa: **<5%**.\n- Ví dụ: Kỹ sư AI, Thiết kế.")

    with tabs[3]:
        st.header("4. Thiết lập Ma trận Xác suất (P)")
        st.markdown("Điều chỉnh các tham số chính sách (Training/Reskilling) để thay đổi dòng dịch chuyển:")
        
        reskill_eff = st.slider("Hiệu quả chương trình Đào tạo lại (Reskilling Efficiency)", 0.0, 1.0, 0.4)
        auto_speed = st.slider("Tốc độ tự động hóa ngành công nghệ (Automation Speed)", 0.0, 1.0, 0.2)
        
        # Define Transition Matrix based on sliders
        # Rows: Manual, Cognitive, AI-Hybrid, Unemployed
        # Columns: Same
        P = np.array([
            [0.7 - auto_speed*0.5, 0.1, 0.05 * reskill_eff, 0.15 + auto_speed*0.4], # Manual moves
            [0.0, 0.6 - auto_speed*0.3, 0.2 * reskill_eff, 0.2 + auto_speed*0.2],   # Cognitive moves
            [0.0, 0.0, 0.95, 0.05],                                                # AI-Hybrid stays
            [0.05 * reskill_eff, 0.05 * reskill_eff, 0.0, 0.9]                     # Unemployed return
        ])
        
        st.write("Ma trận xác suất chuyển đổi (P):")
        st.table(pd.DataFrame(P, 
                             index=['From Manual', 'From Cog', 'From AI', 'From Unemp'],
                             columns=['To Manual', 'To Cog', 'To AI', 'To Unemp']))

    with tabs[4]:
        st.header("5. Trực quan hóa dòng lao động (Sankey Diagram)")
        
        # Initial Population (Millions)
        L0 = np.array([35.0, 15.0, 2.0, 2.0]) # Manual, Cog, AI, Unemp
        L1 = L0 @ P
        
        # Create Sankey links
        labels = ["Manual (T0)", "Cognitive (T0)", "AI-Hybrid (T0)", "Unemployed (T0)",
                  "Manual (T1)", "Cognitive (T1)", "AI-Hybrid (T1)", "Unemployed (T1)"]
        
        sources = []
        targets = []
        values = []
        
        for i in range(4):
            for j in range(4):
                val = L0[i] * P[i, j]
                if val > 0.01:
                    sources.append(i)
                    targets.append(j + 4)
                    values.append(val)
        
        fig = go.Figure(data=[go.Sankey(
            node = dict(pad = 15, thickness = 20, line = dict(color = "black", width = 0.5),
                        label = labels, color = ["blue", "orange", "green", "red"]*2),
            link = dict(source = sources, target = targets, value = values,
                        color = "rgba(200, 200, 200, 0.4)")
        )])
        
        fig.update_layout(title_text="Dòng dịch chuyển nhân lực sau 1 năm ứng dụng AI mạnh mẽ", font_size=10)
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric("Tỷ lệ thất nghiệp dự báo (Unemployed T1)", f"{L1[3]:.2f} Triệu", 
                  f"{(L1[3]-L0[3])/L0[3]*100:.1f}% so với ban đầu")

    with tabs[5]:
        st.header("6. Thảo luận chính sách")
        st.markdown("""
        - **Cú sốc Manual:** Nếu tốc độ tự động hóa cao mà hiệu quả đào tạo (`reskill_eff`) thấp, số lượng lao động Unemployed sẽ bùng nổ từ nhóm Manual.
        - **Nút thắt AI-Hybrid:** Nhóm này có mức độ ổn định cao nhất, nhưng "đầu vào" chuyển từ các nhóm khác sang rất hẹp (đòi hỏi chi phí đào tạo lớn).
        - **Khuyến nghị:** Cần xây dựng các "cầu nối" kỹ năng từ Cognitive sang AI-Hybrid thay vì chỉ tập trung cứu trợ thất nghiệp.
        """)
        
    with tabs[6]:
        st.header("Tham khảo")
        st.markdown("""
        - **MIT Task Model (Acemoglu & Restrepo):** The Race between Machine and Man.
        - **ILO Report 2030:** Artificial Intelligence and the Future of Work in Vietnam.
        - **Markov Chain Applications** in Social Sciences.
        """)

if __name__ == "__main__":
    render()
