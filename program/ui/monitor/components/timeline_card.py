#
# program/ui/monitor/components/timeline_card.py
#
# Trade Timeline Card
#
# 役割:
#   ・Trade Timelineを表示
#

import streamlit as st

from ui.utils.ui_labels import (
    TIMELINE_EVENT_LABEL,
    TIMELINE_EVENT_UNKNOWN,
)

from ui.utils.formatters import (
    fmt_dt,
    fmt_price,
)

def render_timeline_card(timeline):

    with st.container(border=True):

        st.markdown("**Timeline**")

        if not timeline:
            st.write("Timelineはありません")
            return

        for index, item in enumerate(reversed(timeline)):

            time_text = fmt_dt(item.get("time"))

            event = item.get("event", "")
            event_text = TIMELINE_EVENT_LABEL.get(
                event,
                TIMELINE_EVENT_UNKNOWN
            )

            message = item.get("message", "")
            current_price = item.get("current_price")

            html = (
                f'<div style="padding:2px 0;">'
                f'<strong>{time_text}　{event_text}　{event}</strong><br>'
                f'{message}'
            )

            if current_price is not None:
                html += (
                    f'<br>価格：{fmt_price(current_price)}'
                )

            html += '</div>'

            st.markdown(
                html,
                unsafe_allow_html=True
            )

            if index < len(timeline) - 1:
                st.markdown(
                    '<hr style="margin:4px 0;">',
                    unsafe_allow_html=True
                )
