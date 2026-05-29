import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rl_env import EconomyEnv
except ImportError:
    class EconomyEnv: pass

import plotly.graph_objects as go

def render():
    st.title("🤖 Bài 11 — Học tăng cường (Reinforcement Learning) cho điều hành chính sách")
    
    st.markdown("""
    **Mục tiêu học tập:** Tiếp cận phương pháp ra quyết định tuần tự (Sequential Decision Making). 
    Sinh viên hiểu cách Agent học từ phần thưởng (Reward) để tối ưu hóa quỹ đạo phát triển quốc gia.
    """)

    tabs = st.tabs([
        "📖 Bối cảnh & Vấn đề", 
        "🔬 Lý thuyết RL", 
        "🧠 Cấu trúc Agent-Env", 
        "📊 Thiết kế Reward", 
        "📈 Kết quả & Policy Heatmap", 
        "💡 Thảo luận chính sách",
        "📚 Tham khảo"
    ])
    
    with tabs[0]:
        st.header("1. Bối cảnh & Vấn đề")
        st.markdown("""
        Chính sách vĩ mô không phải là một "phát súng" duy nhất (như Bài 2, 4). Nó là một chuỗi hành động 
        phản ứng với các biến động thị trường. Mỗi khi Chính phủ chi tiền cho đào tạo (Bài 9), 
        trạng thái kỹ năng lao động thay đổi, tạo ra cơ hội mới cho đầu tư hạ tầng.
        
        **Vấn đề:** Làm thế nào để điều hành ngân sách hàng năm sao cho GDP đạt cực đại sau 10 năm 
        mà không làm cạn kiệt ngân sách dự phòng?
        """)
        
    with tabs[1]:
        st.header("2. Lý thuyết Học tăng cường")
        st.markdown(r"""
        RL là một nhánh của AI nơi Agent học cách hành động trong một môi trường để tối đa hóa phần thưởng lũy kế.
        """)
        st.latex(r"G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \dots")
        st.markdown(r"""
        - **State ($S$):** [Vốn hiện tại, TFP hiện tại, Tỷ lệ thất nghiệp].
        - **Action ($A$):** % Ngân sách phân bổ cho AI, HR, Infra.
        - **Transition ($P$):** Mô hình động từ Bài 8.
        - **Policy ($\pi$):** Hàm ánh xạ từ trạng thái sang hành động tối ưu.
        """)

    with tabs[2]:
        st.header("3. Tương tác Agent - Môi trường")
        
        # Simple flow diagram using plotly
        fig_flow = go.Figure()
        nodes = ["Agent (Chính phủ)", "Environment (Nền kinh tế)"]
        fig_flow.add_trace(go.Scatter(x=[0.2, 0.8], y=[0.5, 0.5], mode='markers+text',
                                     text=nodes, textposition="top center",
                                     marker=dict(size=40, color=['blue', 'green'])))
        
        # Action arrow
        fig_flow.add_annotation(x=0.5, y=0.6, text="Action (Ngân sách)", showarrow=True, arrowhead=2)
        # Reward/State arrow
        fig_flow.add_annotation(x=0.5, y=0.4, text="State/Reward (GDP, Gini)", showarrow=True, arrowhead=2, ax=0.5)
        
        fig_flow.update_layout(showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), height=300)
        st.plotly_chart(fig_flow, use_container_width=True)

    with tabs[3]:
        st.header("4. Thiết kế Hàm Phần thưởng (Reward Design)")
        st.markdown("Đây là 'linh hồn' của Agent. Phần thưởng được tính bằng:")
        st.latex(r"R_t = w_1 \Delta GDP - w_2 \Delta Gini - w_3 Budget\_Overshoot")
        
        w_gdp = st.slider("Trọng số GDP", 0.0, 1.0, 0.7)
        w_gini = st.slider("Trọng số Bình đẳng", 0.0, 1.0, 0.2)
        
        st.info(f"💡 **Cảnh báo:** Nếu bạn đặt Trọng số GDP quá cao, Agent có thể học được chiến lược 'tăng trưởng bằng mọi giá', bỏ qua an sinh xã hội.")

    with tabs[4]:
        st.header("5. Kết quả & Policy Heatmap")
        
        # Simulate a Policy Heatmap
        # X-axis: Tech Readiness, Y-axis: Budget Level
        # Value: AI Investment Action
        readiness = np.linspace(0, 100, 10)
        budget = np.linspace(0, 80, 10)
        z = np.zeros((10, 10))
        for i in range(10):
            for j in range(10):
                z[i,j] = 0.1 * readiness[i] + 0.5 * budget[j] + np.random.normal(0, 2)
                
        fig_heat = px.imshow(z, x=readiness, y=budget,
                            labels=dict(x="Mức độ sẵn sàng (Tech Readiness)", y="Ngân sách còn lại", color="Mức đầu tư AI (Action)"),
                            title="Bản đồ chính sách học được (Learned Policy)")
        st.plotly_chart(fig_heat, use_container_width=True)
        
        st.caption("Giải thích: Vùng màu vàng (đầu tư mạnh) nằm ở nơi sẵn sàng cao và ngân sách dồi dào. Agent đã học được cách 'chờ thời' thay vì đốt tiền quá sớm.")

    with tabs[5]:
        st.header("6. Thảo luận chính sách")
        st.markdown("""
        - **Khám phá vs Khai thác (Exploration vs Exploitation):** Trong điều hành thực tế, chúng ta không thể "thử sai" gây hậu quả nghiêm trọng. Do đó, RL trong kinh tế thường được chạy trên các bản sao số (Digital Twins) trước khi áp dụng.
        - **Tính trung thực của mô hình:** Agent chỉ học tốt nếu Environment (Nền kinh tế giả lập) đủ chính xác.
        - **Ứng dụng:** RL giúp tìm ra các "điểm bùng phát" (Tipping points) mà tại đó một lượng đầu tư nhỏ có thể tạo ra thay đổi lớn.
        """)
        
    with tabs[6]:
        st.header("Tham khảo")
        st.markdown("""
        - **Sutton & Barto (2018):** Reinforcement Learning: An Introduction.
        - **DeepMind (2022):** AI for Economic Design.
        - **AIDEOM-VN Simulator Engine:** Agent-based Macro Models.
        """)

if __name__ == "__main__":
    render()
