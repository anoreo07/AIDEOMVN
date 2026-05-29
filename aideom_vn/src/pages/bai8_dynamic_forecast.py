import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def render():
    st.title("⏳ Bài 8 — Mô hình động: Dự báo vốn tích lũy và tăng trưởng kinh tế số 2026-2035")
    
    st.markdown(r"""
    **Mục tiêu học tập:** Tiếp cận mô hình dự báo động (Recursive forecasting). 
    Sinh viên hiểu cách vốn $K$ tích lũy theo thời gian và tác động của độ trễ (time-lag) trong đầu tư công nghệ.
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Cấu trúc", 
        "🔬 Lý thuyết Hệ thống Động", 
        "🧠 Vector Trạng thái", 
        "📈 Dự báo 2026-2035", 
        "💡 Phân tích Chu kỳ",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Cấu trúc")
        st.markdown("""
        Đầu tư vào AI và Hạ tầng số không giống như đầu tư vào tiêu dùng; nó tạo ra một lượng **Vốn số (Digital Capital)** 
        có khả năng tái sản xuất và thúc đẩy năng suất lao động trong dài hạn. 
        
        **Vấn đề:** Với ngân sách 80.000 tỷ VND (từ Bài 5) được giải ngân trong 5 năm đầu, 
        tác động của nó đến tổng vốn quốc gia và GDP sẽ diễn biến thế nào đến năm 2035? 
        Mô hình cần tính đến tốc độ khấu hao của công nghệ (thường nhanh hơn vốn hữu hình).
        """)
        
    with tabs[1]:
        st.header("2. Lý thuyết Vốn tích lũy")
        st.markdown("Sử dụng phương trình tích lũy vốn cơ bản trong kinh tế học tăng trưởng:")
        st.latex(r"K_{t+1} = K_t(1 - \delta) + I_t")
        st.markdown("""
        Trong đó:
        - $K_t$: Trữ lượng vốn tại năm $t$.
        - $\delta$: Tỷ lệ khấu hao (Depreciation rate). Với thiết bị công nghệ và phần mềm, $\delta \approx 15-20\%$.
        - $I_t$: Đầu tư mới từ ngân sách nhà nước và tư nhân.
        """)
        st.markdown("Sản lượng GDP được dự báo thông qua hàm sản xuất mở rộng:")
        st.latex(r"Y_t = A_t \cdot K_t^\alpha \cdot L_t^{1-\alpha}")

    with tabs[2]:
        st.header("3. Thiết lập Vector Trạng thái & Tham số")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Tham số kinh tế:**")
            delta = st.slider("Tỷ lệ khấu hao vốn số (%)", 5, 25, 12) / 100
            alpha = st.slider("Hệ số co giãn của vốn (α)", 0.3, 0.6, 0.45)
        with col2:
            st.markdown("**Tham số kịch bản:**")
            inv_efficiency = st.slider("Hiệu quả đầu tư (Incremental OR)", 1.5, 4.0, 2.8)
            tfp_base = st.slider("Tăng trưởng TFP tự nhiên (%)", 1.0, 4.0, 2.2) / 100

    with tabs[3]:
        st.header("4. Dự báo đa kịch bản 2026-2035")
        
        years = np.arange(2025, 2036)
        
        def simulate_growth(scenario_name, annual_inv):
            k_history = [100000] # Initial Digital Capital 2025 (mô phỏng)
            gdp_history = [12847]
            
            for i in range(1, len(years)):
                # Investment lag: giả định đầu tư năm trước tạo vốn năm sau
                i_t = annual_inv if years[i] <= 2030 else annual_inv * 0.5 
                k_new = k_history[-1] * (1 - delta) + i_t
                k_history.append(k_new)
                
                # GDP growth based on capital and TFP
                growth = (alpha * (k_new/k_history[-2] - 1) + tfp_base)
                gdp_new = gdp_history[-1] * (1 + growth)
                gdp_history.append(gdp_new)
                
            return pd.DataFrame({
                'Year': years, 
                'Capital': k_history, 
                'GDP': gdp_history,
                'Scenario': scenario_name
            })
            
        df_base = simulate_growth("Cơ bản (80k tỷ)", 16000)
        df_high = simulate_growth("Đột phá (120k tỷ)", 24000)
        df_low = simulate_growth("Thận trọng (40k tỷ)", 8000)
        
        df_all = pd.concat([df_base, df_high, df_low])
        
        fig_gdp = px.line(df_all, x='Year', y='GDP', color='Scenario', 
                          title="Tương quan GDP theo các kịch bản giải ngân ngân sách",
                          line_dash='Scenario')
        st.plotly_chart(fig_gdp, use_container_width=True)
        
        fig_cap = px.area(df_all[df_all['Scenario']=='Cơ bản (80k tỷ)'], x='Year', y='Capital',
                          title="Diễn biến tích lũy vốn số (Kịch bản Cơ bản)")
        st.plotly_chart(fig_cap, use_container_width=True)

    with tabs[4]:
        st.header("5. Phân tích chu kỳ & Điểm dừng")
        st.markdown("""
        - **Giai đoạn 2026-2030 (Giải ngân mạnh):** Trữ lượng vốn tăng vọt, GDP tăng trưởng nhanh nhờ cú hích đầu tư trực tiếp.
        - **Giai đoạn 2031-2035 (Sau giải ngân):** Tốc độ tăng trưởng chậm lại do tác động của khấu hao. Nếu không có đầu tư duy trì, trữ lượng vốn sẽ hội tụ về 'Trạng thái dừng' (Steady State).
        - **Bài học:** Chính phủ cần duy trì cơ chế đầu tư tái tạo (Re-investment) để bù đắp lượng vốn số bị lỗi thời theo năm tháng.
        """)
        
    with tabs[5]:
        st.header("Tham khảo")
        st.markdown("""
        - **Solow, R. M. (1956).** A Contribution to the Theory of Economic Growth.
        - **Sách trắng Kinh tế số Việt Nam 2024.**
        - Dynamic Stochastic General Equilibrium (DSGE) Models for Emerging Markets.
        """)

if __name__ == "__main__":
    render()
