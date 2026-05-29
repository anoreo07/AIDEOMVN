import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def render():
    st.title("🌐 Bài 7 — Tối ưu hóa đa mục tiêu (Multi-Objective Optimization)")
    
    st.markdown("""
    **Mục tiêu học tập:** Sinh viên nắm vững khái niệm biên tối ưu Pareto và giải thuật di truyền NSGA-II. 
    Hiểu được ranh giới của sự "đánh đổi" giữa các mục tiêu kinh tế - xã hội xung đột nhau 
    trong kỷ nguyên AI.
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Vấn đề", 
        "🔬 Lý thuyết Pareto", 
        "🧠 Cấu trúc 3 Mục tiêu", 
        "📈 Không gian Pareto 3D", 
        "🔥 So sánh các kịch bản",
        "💡 Thảo luận chính sách",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Trong quản trị quốc gia, Chính phủ thường phải đối mặt với các mục tiêu "nghịch biến" với nhau. 
        Ví dụ: Để thúc đẩy tăng trưởng GDP cực nhanh thông qua AI, ta có thể phải chấp nhận rủi ro an ninh mạng cao 
        hoặc sự nới rộng khoảng cách thu nhập (Gini) do thay thế lao động.
        
        **Vấn đề:** Tìm tập hợp các phương án phân bổ ngân sách AI (Pareto Front) sao cho không thể cải thiện 
        hơn một mục tiêu này mà không làm tệ đi ít nhất một mục tiêu khác.
        """)
        st.info("💡 **Thách thức:** Không có kịch bản 'hoàn hảo', chỉ có kịch bản 'tối ưu trong đánh đổi'.")
        
    with tabs[1]:
        st.header("2. Lý thuyết NSGA-II")
        st.markdown(r"""
        NSGA-II (*Non-dominated Sorting Genetic Algorithm II*) là thuật toán di truyền phổ biến nhất để giải các bài toán tối ưu đa mục tiêu.
        """)
        
        st.latex(r"\min F(x) = [f_1(x), f_2(x), f_3(x)]^T")
        
        st.markdown(r"""
        **Các khái niệm then chốt:**
        - **Không lấn át (Non-dominance):** Phương án A lấn át B nếu A tốt hơn B ở ít nhất một mục tiêu và không tệ hơn ở bất kỳ mục tiêu nào khác.
        - **Mặt trận Pareto (Pareto Front):** Tập hợp tất cả các phương án không bị lấn át bởi bất kỳ phương án nào khác.
        - **Khoảng cách đám đông (Crowding Distance):** Cơ chế giúp duy trì sự đa dạng của các nghiệm trên mặt trận Pareto.
        """)
        st.latex(r"\min F(x) = [f_1(x), f_2(x), f_3(x)]")

    with tabs[2]:
        st.header("3. Các mục tiêu xung đột")
        st.markdown("Giả định ta có 5 lĩnh vực đầu tư ($I, D, AI, H, G$). Phương án là vector trọng số phân bổ.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mục tiêu 1", "Max GDP Gain", "Benefit (+)")
            st.caption("Ưu tiên AI và Infra")
        with col2:
            st.metric("Mục tiêu 2", "Min Gini Impact", "Cost (-)")
            st.caption("Ưu tiên Đào tạo (HR)")
        with col3:
            st.metric("Mục tiêu 3", "Min Risk Score", "Cost (-)")
            st.caption("Ưu tiên Quản trị (Gov)")

    with tabs[3]:
        st.header("4. Trực quan hóa Không gian Pareto 3D")
        
        # Simulation of a Pareto Front
        n_pareto = 200
        u = np.random.rand(n_pareto)
        v = np.random.rand(n_pareto)
        
        # Theoretical Pareto Surface: f1^2 + f2^2 + f3^2 = 1 (approx)
        f1 = u * v
        f2 = u * (1-v)
        f3 = 1 - u
        
        # Add some noise and scale to realistic VN context
        gdp_gain = 3 + 7 * f1 + np.random.normal(0, 0.1, n_pareto)
        gini_inc = 0.01 + 0.05 * f2 + np.random.normal(0, 0.001, n_pareto)
        risk_score = 10 + 50 * f3 + np.random.normal(0, 1, n_pareto)
        
        df_p = pd.DataFrame({
            'GDP_Gain (%)': gdp_gain,
            'Gini_Impact': gini_inc,
            'Risk_Score': risk_score,
            'Scenario': [f"Method {i+1}" for i in range(n_pareto)]
        })
        
        fig_3d = px.scatter_3d(df_p, x='GDP_Gain (%)', y='Gini_Impact', z='Risk_Score',
                               color='GDP_Gain (%)', opacity=0.8,
                               title="Biên Pareto 3D cho Chiến lược AI 2030",
                               color_continuous_scale='Viridis')
        st.plotly_chart(fig_3d, use_container_width=True)
        st.caption("Giải thích: Các điểm trên mặt phẳng này là các lựa chọn tối ưu. Di chuyển từ góc này sang góc kia đòi hỏi sự đánh đổi mục tiêu.")

    with tabs[4]:
        st.header("5. Phân tích lát cắt (Parallel Coordinates)")
        st.markdown("Công cụ giúp so sánh 3 kịch bản điển hình trên biên Pareto:")
        
        # Highlight specific scenarios
        df_top = df_p.sort_values('GDP_Gain (%)', ascending=False).head(1).copy()
        df_top['Strategy'] = 'Aggressive (Tăng trưởng)'
        df_soc = df_p.sort_values('Gini_Impact', ascending=True).head(1).copy()
        df_soc['Strategy'] = 'Social (Bình đẳng)'
        df_safe = df_p.sort_values('Risk_Score', ascending=True).head(1).copy()
        df_safe['Strategy'] = 'Safe (An toàn)'
        
        df_comp = pd.concat([df_top, df_soc, df_safe])
        
        fig_par = px.parallel_coordinates(df_comp, color="GDP_Gain (%)",
                             dimensions=['GDP_Gain (%)', 'Gini_Impact', 'Risk_Score'],
                             color_continuous_scale=px.colors.diverging.Tealrose,
                             color_continuous_midpoint=5)
        st.plotly_chart(fig_par, use_container_width=True)

    with tabs[5]:
        st.header("6. Thảo luận chính sách")
        st.markdown("""
        - **Kịch bản Tăng trưởng (Aggressive):** Đạt GDP Gain > 8% nhưng Risk Score vọt lên trên 50 và Gini tăng mạnh. Phù hợp khi quốc gia cần bứt phá nhanh về công nghệ.
        - **Kịch bản Bao trùm (Social):** Chấp nhận GDP Gain thấp (4-5%) để giữ Gini ổn định. Phù hợp với các giai đoạn cần ổn định chính trị - xã hội.
        - **Kịch bản Trung dung:** Nằm ở giữa biên Pareto, là lựa chọn phổ biến của các nhà kỹ trị.
        - **Bài học:** Chính sách AI không đơn thuần là kỹ thuật, mà là lựa chọn giá trị xã hội.
        """)
        
    with tabs[6]:
        st.header("Tham khảo")
        st.markdown("""
        - **Deb, K. (2001).** Multi-Objective Optimization using Evolutionary Algorithms.
        - **Pymoo library documentation:** Multi-objective Framework for Python.
        - **World Economic Forum (2024):** Balancing AI Innovation and Risk.
        - **Deb, K. (2002).** A fast and elitist multiobjective genetic algorithm: NSGA-II.
        - **UNDP:** AI for Social Good report.
        - **AIDEOM-VN Research**, Section 8.
        """)

if __name__ == "__main__":
    render()
