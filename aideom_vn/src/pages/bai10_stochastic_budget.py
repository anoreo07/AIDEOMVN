import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from m5_risk import va_risk_analysis
except ImportError:
    def va_risk_analysis(*args, **kwargs): return {}

def render():
    st.title("🎲 Bài 10 — Tối ưu hóa ngẫu nhiên: Quản trị rủi ro ngân sách AI")
    
    st.markdown("""
    **Mục tiêu học tập:** Tiếp cận mô hình ra quyết định trong điều kiện bất định (Uncertainty). 
    Sinh viên hiểu cách xây dựng mô hình 2 giai đoạn (Two-stage) và các khái niệm: 
    Giá trị của thông tin hoàn hảo (EVPI) và Giá trị của giải pháp ngẫu nhiên (VSS).
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Cấu trúc", 
        "🔬 Lý thuyết Two-stage", 
        "🧠 Cây kịch bản (Scenario Tree)", 
        "📊 Bài toán phân bổ", 
        "📈 Kết quả Tối ưu ngẫu nhiên", 
        "💡 Thảo luận chính sách",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Lập kế hoạch ngân sách AI 5 năm là một bài toán mạo hiểm. Thế giới có thể rơi vào suy thoái (Bi quan), 
        duy trì ổn định (Cơ sở), hoặc bùng nổ công nghệ vượt bậc (Lạc quan). 
        
        **Vấn đề:** 
        - **Giai đoạn 1 (Nay):** Quyết định đầu tư vào Hạ tầng (P1, P3). 
        - **Giai đoạn 2 (2028):** Sau khi biết kịch bản kinh tế thực tế, ta sẽ điều chỉnh đầu tư vào Ứng dụng và Đào tạo. 
        Mục tiêu là tìm quyết định GĐ1 sao cho tổng lợi ích kỳ vọng là lớn nhất.
        """)
        st.info("💡 **Hành động hiện tại** phải tính đến các **khả năng trong tương lai**.")
        
    with tabs[1]:
        st.header("2. Lý thuyết Two-stage Stochastic Programming")
        st.markdown(r"Mô hình bao gồm các quyết định 'Here-and-Now' và 'Wait-and-See'.")
        st.latex(r"\max Z = c^T x + \sum_{s \in S} p_s [q_s^T y_s]")
        st.markdown(r"""
        - $x$: Quyết định giai đoạn 1 (không phụ thuộc kịch bản).
        - $y_s$: Quyết định giai đoạn 2 (thích ứng với kịch bản $s$).
        - $p_s$: Xác suất xảy ra kịch bản $s$.
        - Ràng buộc: $Ax = b$ và $T_s x + W_s y_s = h_s$.
        """)

    with tabs[2]:
        st.header("3. Xây dựng Cây kịch bản")
        import plotly.graph_objects as go
        
        # Scenario data
        scenarios = {
            "Lạc quan (P=0.2)": {"growth": "8.5%", "color": "green", "impact": 1.4},
            "Cơ sở (P=0.6)": {"growth": "6.5%", "color": "blue", "impact": 1.0},
            "Bi quan (P=0.2)": {"growth": "4.0%", "color": "red", "impact": 0.6}
        }
        
        # Drawing a simple tree-like figure using plotly
        fig_tree = go.Figure()
        # Root to nodes
        fig_tree.add_trace(go.Scatter(x=[0, 1, 1, 1], y=[0, 1, 0, -1], mode='lines+markers+text',
                                     text=["GĐ1 (Now)", "Lạc quan", "Cơ sở", "Bi quan"],
                                     textposition="top right",
                                     marker=dict(size=[20, 15, 15, 15], color=['black', 'green', 'blue', 'red'])))
        fig_tree.update_layout(title="Cấu trúc cây quyết định 2 giai đoạn", showlegend=False,
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
        st.plotly_chart(fig_tree, use_container_width=True)

    with tabs[3]:
        st.header("4. Thiết lập bài toán phân bổ")
        st.markdown("""
        Giả sử tổng ngân sách là 80.000 tỷ. 
        - Bạn phải chi $X$ tỷ ngay bây giờ cho AI Infrastructure.
        - Số tiền còn lại $(80-X)$ sẽ được chi cho AI Apps ở GĐ2 tùy theo tình hình.
        """)
        
        x_init = st.slider("Ngân sách chi ngay GĐ1 (Tỷ VND)", 10000, 60000, 30000)
        
        st.markdown("**Hiệu suất sinh lời của AI Apps theo kịch bản:**")
        st.write("- **Lạc quan:** 1 VND đầu tư GĐ2 tạo ra 3.5 VND NPV.")
        st.write("- **Cơ sở:** 1 VND đầu tư GĐ2 tạo ra 2.2 VND NPV.")
        st.write("- **Bi quan:** 1 VND đầu tư GĐ2 tạo ra 0.8 VND NPV.")

    with tabs[4]:
        st.header("5. Phân tích Giá trị Thông tin (EVPI)")
        
        # Calculate Expectation
        rem = 80000 - x_init
        npv_options = {
            "Lạc quan": x_init * 1.5 + rem * 3.5,
            "Cơ sở": x_init * 1.5 + rem * 2.2,
            "Bi quan": x_init * 1.5 + rem * 0.8
        }
        
        ev = 0.2 * npv_options["Lạc quan"] + 0.6 * npv_options["Cơ sở"] + 0.2 * npv_options["Bi quan"]
        
        st.metric("Lợi ích kỳ vọng (Expected Value)", f"{ev:,.0f} Tỷ VND")
        
        # Plotting the risk
        df_npv = pd.DataFrame({
            "Kịch bản": npv_options.keys(),
            "NPV": npv_options.values(),
            "Xác suất": [0.2, 0.6, 0.2]
        })
        
        fig_bins = px.bar(df_npv, x='Kịch bản', y='NPV', color='Kịch bản', 
                          title="Biến động lợi ích theo kịch bản với quyết định hiện tại")
        st.plotly_chart(fig_bins, use_container_width=True)
        
        st.info(f"""
        💡 **Phân tích:** Nếu bạn biết trước kịch bản 'Bi quan' sẽ xảy ra, bạn nên tăng $X$ (Infrastructure) vì 
        lúc đó đầu tư vào App (GĐ2) sinh lời rất thấp (0.8 < 1). Ngược lại, nếu biết 'Lạc quan', 
        bạn nên dồn hết tiền cho GĐ2.
        """)

    with tabs[5]:
        st.header("6. Thảo luận chính sách")
        st.markdown("""
        - **Phòng vệ ròng (Hedging):** Quyết định Stochastic thường chọn mức $X$ trung dung để khi kịch bản xấu xảy ra ta không mất quá nhiều, và khi kịch bản tốt xảy ra ta vẫn có bàn đạp để phát triển.
        - **Tính linh hoạt (Optionality):** Chính sách AI bền vững là chính sách cho phép điều chỉnh (Recourse) ở giai đoạn 2 thay vì chốt cứng mọi hạng mục ngay từ năm đầu tiên.
        - **VSS (Value of Stochastic Solution):** Là số tiền Chính phủ tiết kiệm được/lợi ích tăng thêm khi thực hiện giải pháp ngẫu nhiên so với giải pháp chỉ dựa trên kịch bản trung bình.
        """)
        
    with tabs[6]:
        st.header("Tham khảo")
        st.markdown("""
        - **Shapiro, A., et al. (2021).** Lectures on Stochastic Programming.
        - **Kall & Wallace:** Stochastic Programming (Classic).
        - **Vietnam Economic Outlook 2026-2030 (World Bank).**
        """)

if __name__ == "__main__":
    render()
