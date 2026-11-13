// Lists the focused pane's ids. Press 1-7 to copy one, a to copy all on one
// line, q or Esc to close. Opened with mod.open:ids (keys.json: ctrl-a i).

import { View, div } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { focused, spaces, panes, props, closeOverlay, notify, theme } from "herdr";
import { allLine, idRows } from "./rows.js";

export default class Ids extends View {
  init(_props, cx) {
    this.rows = idRows(focused(), spaces(), panes());
    this.handle = cx.focus_handle();
    this.handle.focus();
  }

  copy(cx, label, text) {
    cx.write_to_clipboard(text);
    closeOverlay(props().overlay);
    notify({ title: `Copied ${label}`, body: text, level: "success", timeout: 2000 });
  }

  onKey(e, cx) {
    const k = e.key;
    if (k === "escape" || k === "q") closeOverlay(props().overlay);
    else if (k === "a" && this.rows.length) {
      this.copy(cx, "all ids", allLine(this.rows));
    } else if (/^[1-9]$/.test(k) && this.rows[Number(k) - 1]) {
      const [label, value] = this.rows[Number(k) - 1];
      this.copy(cx, label, value);
    } else return;
    cx.stop_propagation();
  }

  row(t, i, [label, value, note]) {
    return h_flex()
      .id(`ids-row-${i}`)
      .gap(12)
      .px(8)
      .py(4)
      .rounded(6)
      .cursor_pointer()
      .hover((s) => s.bg(t.hover))
      .on_click((_e, cx) => this.copy(cx, label, value))
      .child(div().w(14).flex_none().text_color(t.accent).font_semibold().child(String(i + 1)))
      .child(div().w(70).flex_none().text_color(t.muted).child(label))
      .child(div().flex_1().min_w(0).truncate().text_color(t.foreground).child(value))
      .when(Boolean(note), (el) => el.child(div().flex_none().max_w(140).truncate().text_color(t.dim).child(note)));
  }

  render(cx) {
    const t = theme();
    const hint = (key, label) => h_flex().gap(6).child(div().text_color(t.accent).font_semibold().child(key)).child(div().text_color(t.dim).child(label));
    return v_flex()
      .id("ids")
      .track_focus(this.handle)
      .on_key_down((e, cx) => this.onKey(e, cx))
      .size_full()
      .p(14)
      .gap(8)
      .rounded(8)
      .bg(t.popover)
      .text_size(13)
      .child(div().text_size(15).font_semibold().text_color(t.foreground).child("herdr ids"))
      .when(this.rows.length === 0, (el) => el.child(div().text_color(t.muted).child("Nothing focused.")))
      .child(v_flex().gap(2).children(this.rows.map((r, i) => this.row(t, i, r))))
      .child(h_flex().gap(16).pt(4).text_size(12).child(hint(`1-${this.rows.length}`, "copy one")).child(hint("a", "all, one line")).child(hint("q", "close")));
  }
}
