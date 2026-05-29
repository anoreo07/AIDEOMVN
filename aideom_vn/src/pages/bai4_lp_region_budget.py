import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from m3_allocation import solve_allocation_pulp
except ImportError:
    def solve_allocation_pulp(*args, **kwargs): return np.zeros((6,4)), 0.0

def render():
    st.title("🗺️ Bài 4 — Quy hoạch tuyến tính phân bổ ngân sách số theo ngành - vùng")
    
    st.markdown(r"""
    **Mục tiêu học tập:** Sinh viên mở rộng được bài toán LP lên quy mô 24 biến quyết định, thực hiện 
    tuyến tính hóa ràng buộc cực đại (minimax/maximin) để đảm bảo công bằng vùng miền ($\lambda$ equity), 
    và phân tích được "chi phí của sự công bằng" (cost of equity).
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Vấn đề", 
        "🔬 Mô hình LP Đa vùng", 
        "🧠 Chỉ số Số hóa Vùng", 
        "📊 Ma trận hệ số Beta", 
        "📈 Kết quả tối ưu hóa", 
        "💡 Thảo luận chính sách",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Theo Quyết định số 411/QĐ-TTg, các vùng kinh tế xã hội (KTXH) của Việt Nam có mức độ sẵn sàng số rất khác nhau. 
        Trong khi Đồng bằng sông Hồng (ĐBSH) và Đông Nam Bộ (ĐNB) dẫn đầu, các vùng như Tây Nguyên và Miền núi phía Bắc (MNPB) 
        đối mặt rủi ro tụt hậu hay "khoảng cách số" (digital divide).
        
        **Vấn đề:** Phân bổ **50.000 tỷ VND** cho 6 vùng và 4 hạng mục đầu tư ($I, D, AI, H$) sao cho tối ưu GDP gain 
        nhưng không để vùng nào bị bỏ lại quá xa.
        """)
        st.info("💡 **Thách thức:** Cân bằng giữa Hiệu quả (Efficiency) và Công bằng (Equity).")
        
    with tabs[1]:
        st.header("2. Mô hình tối ưu hóa")
        st.markdown(r"""
        Bài toán được mô hình hóa dưới dạng **Quy hoạch tuyến tính (Linear Programming)** với 24 biến quyết định.
        Mục tiêu là tối đa hóa tổng lợi ích xã hội $Z$:
        """)
        st.latex(r"max Z = \sum_{r=1}^6 \sum_{j=1}^4 w_j \cdot x_{j,r}")
        st.markdown(r"""
        Trong đó $x_{j,r}$ là ngân sách cho hạng mục $j$ tại vùng $r$.
        
        **Các ràng buộc chính:**
        """)
        st.markdown(r"- $j \in \{1: I, 2: D, 3: AI, 4: H\}$")
        st.markdown(r"- $r \in \{1, 2, 3, 4, 5, 6\}$")
        st.markdown(r"""
        1. **Ngân sách tổng:** $\sum_r \sum_j x_{j,r} \leq 50.000$ (tỷ VND)
        2. **Ngân sách tối thiểu mỗi vùng:** $\sum_j x_{j,r} \geq B_r^{min}$
        3. **Sàn hạ tầng:** Tổng đầu tư hạ tầng toàn quốc $\geq$ 10.000 tỷ VND.
        4. **Ràng buộc công bằng (Equity):** Khoảng cách chỉ số số hóa giữa vùng cao nhất và thấp nhất không quá 20%.
        """)
        st.latex(r"\max(D_r^{final}) - \min(D_r^{final}) \leq 0.20")
        st.markdown(r"Trong đó $D_r^{final} = D_r^{init} + \gamma \cdot x_{2,r}$ là chỉ số số hóa của vùng $r$ sau khi nhận đầu tư $x_{2,r}$.")

    with tabs[2]:
        st.header("3. Hiện trạng Chỉ số Số hóa Vùng ($D_r^{init}$)")
        st.markdown("Số liệu giả định dựa trên báo cáo kinh tế số của MIC 2024:")
        
        regions = ['MNPB', 'ĐBS Hồng', 'Bắc Trung Bộ', 'Tây Nguyên', 'Đông Nam Bộ', 'ĐBS Cửu Long']
        d0 = [12.5, 24.8, 15.2, 11.8, 28.5, 14.5]
        
        df_d0 = pd.DataFrame({"Vùng": regions, "D_init (%)": d0})
        fig_d0 = px.bar(df_d0, x="Vùng", y="D_init (%)", color="Vùng", title="Mức độ số hóa ban đầu")
        st.plotly_chart(fig_d0, use_container_width=True)

    with tabs[3]:
        st.header("4. Ma trận hệ số tác động $\beta_{j,r}$")
        items = ['Hạ tầng (I)', 'Ưùng dụng (D)', 'AI/Dữ liệu (AI)', 'Nhân lực (H)']
        beta_vals = [
            [1.25, 0.90, 0.60, 1.35], # MNPB - Hiệu quả hạ tầng/nhân lực cao
            [0.95, 1.25, 1.45, 1.05], # ĐBSH - Hiệu quả công nghệ cao
            [1.10, 1.00, 0.85, 1.20], # BTB
            [1.30, 0.85, 0.55, 1.40], # Tây Nguyên
            [0.90, 1.35, 1.60, 1.00], # ĐNB - Hiệu quả AI cao nhất
            [1.15, 0.95, 0.75, 1.25]  # ĐBSCL
        ]
        df_beta = pd.DataFrame(beta_vals, index=regions, columns=items)
        st.table(df_beta.style.highlight_max(axis=0, color='#10b981'))
        st.caption("Ghi chú: $x_{j,r}$ càng cao tại nơi $\beta_{j,r}$ lớn thì tổng GDP gain càng tăng.")

    with tabs[4]:
        st.header("5. Kết quả tối ưu hóa đa mục tiêu")
        
        # Fallback data if optimization fails
        df_alloc = pd.DataFrame(np.zeros((6, 4)), index=regions, columns=items)
        
        try:
            import pulp
            
            lambd = st.slider("Hệ số công bằng λ (0: Chỉ quan tâm hiệu quả - 1: Tuyệt đối công bằng)", 0.0, 0.95, 0.70)
            gamma = 0.002 # Hệ số cải thiện số hóa/tỷ VND
            
            prob = pulp.LpProblem("Regional_Allocation", pulp.LpMaximize)
            # 24 vars
            x = pulp.LpVariable.dicts("x", (range(6), range(4)), lowBound=0)
            # Variable for max digitization to linearize fairness
            M = pulp.LpVariable("M", lowBound=0)
            
            prob += pulp.lpSum(beta_vals[r][j] * x[r][j] for r in range(6) for j in range(4)), "Total_Gain"
            
            # Constraints
            prob += pulp.lpSum(x[r][j] for r in range(6) for j in range(4)) <= 50000 # Budget
            for r in range(6):
                prob += pulp.lpSum(x[r][j] for j in range(4)) >= 5000 # Min per region
                # Fairness linearization
                d_final = d0[r] + gamma * x[r][1] # x[r][1] is item D
                prob += d_final <= M
                prob += d_final >= lambd * M
                
            prob += pulp.lpSum(x[r][0] for r in range(6)) >= 10000 # Min infrastructure
            
            prob.solve(pulp.PULP_CBC_CMD(msg=0))
            
            if pulp.LpStatus[prob.status] == 'Optimal':
                x_res = np.array([[pulp.value(x[r][j]) for j in range(4)] for r in range(6)])
                z_val = pulp.value(prob.objective)
                
                st.success(f"GDP Gain tối ưu quốc gia: **{z_val/1000:,.1f}** triệu tỷ VND")
                
                df_alloc = pd.DataFrame(x_res, index=regions, columns=items)
                
                col_a, col_b = st.columns([1.5, 1])
                with col_a:
                    st.write("**Ma trận phân bổ (Tỷ VND):**")
                    st.dataframe(df_alloc.style.format(precision=1).background_gradient(cmap='YlGnBu', axis=None))
                
                with col_b:
                    d_final_vals = [d0[r] + gamma * pulp.value(x[r][1]) for r in range(6)]
                    df_d_final = pd.DataFrame({"Vùng": regions, "D_final (%)": d_final_vals})
                    fig_d_final = px.line_polar(df_d_final, r="D_final (%)", theta="Vùng", line_close=True, title="Công bằng Số hóa sau đầu tư")
                    st.plotly_chart(fig_d_final, use_container_width=True)
            else:
                st.error("Không tìm thấy giải pháp tối ưu cho mức λ này.")
        except ImportError:
            st.error("⚠️ **Xác định thiếu thư viện 'PuLP'**")
            st.markdown("""
            Để chạy mô hình tối ưu hóa này, vui lòng cài đặt thư viện PuLP bằng lệnh sau trong terminal:
            ```bash
            pip install pulp
            ```
            """)

            st.subheader("Cơ cấu đầu tư theo Vùng")
            fig_stack = px.bar(df_alloc.reset_index().melt(id_vars='index'), x='index', y='value', color='variable', 
                               title="Chi tiết hạng mục mỗi vùng", labels={'value':'Tỷ VND', 'index':'Vùng'})
            st.plotly_chart(fig_stack, use_container_width=True)
            
        else:
            st.warning("Không tìm thấy nghiệm tối ưu. Hãy thử giảm hệ số λ.")

    with tabs[5]:
        st.header("6. Thảo luận chính sách")
        st.markdown("""
        **a) Chi phí của sự công bằng (Cost of Equity):**
        - Khi $\lambda$ tăng từ 0 lên 0.9, bạn sẽ thấy tổng GDP Gain giảm xuống. Đây là mức đánh đổi để thu hẹp khoảng cách vùng miền.
        
        **b) Tại sao Miền núi phía Bắc và Tây Nguyên lại nhận được nhiều đầu tư Nhân lực ($H$)?**
        - Do hệ số $\beta_{4,r}$ ở các vùng này cao (1.35-1.40). Đầu tư vào con người ở vùng trũng mang lại tỷ suất lợi ích biên lớn nhất.
        
        **c) Tác động của $\gamma$:**
        - Nếu hiệu quả cải thiện số hóa $\gamma$ tăng lên (nhờ công nghệ mới), ta có thể đạt được công bằng với mức chi phí thấp hơn.
        """)
        
    with tabs[6]:
        st.header("7. Tham khảo")
        st.markdown(r"""
        - Quyết định số 411/QĐ-TTg phê duyệt Chiến lược quốc gia phát triển kinh tế số.
        - World Bank: Vietnam's Digital Infrastructure 2024.
        - Nghiên cứu AIDEOM-VN, Mục 7.3.
        - Quyết định 411/QĐ-TTg (2022) về Chiến lược kinh tế số.
        - Báo cáo MIC 2024 về chỉ số DTI các tỉnh thành.
        - Bertsimas, D., & Tsitsiklis, J. N. (1997): Introduction to Linear Optimization.
        """)

if __name__ == "__main__":
    render()
