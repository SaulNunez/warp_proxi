import sys
import xml.etree.ElementTree as ET

from warp.representation.html.image import Image, ImgAlignTypes
from warp.representation.html.table import ColumnAlignment, TableElement, TableRow, TableColumn
from warp.representation.html.text import (
    AHtmlElement,
    BigTextHtmlElement,
    BoldTextHtmlElement,
    BreakHtmlElement,
    ItalicTextElement,
    ParagraphHtmlElement,
    PreformattedText,
    SmallTextHtmlElement,
    StrongTextHtmlElement,
    TextContent,
    UnderlineTextElement,
)
from warp.representation.input import Input, OptionGroup
from warp.representation.markup import Card
from warp.representation.navigation import (
    AnchorElement,
    Do,
    GoElement,
    NoOpElement,
    OnEvent,
    OnPick,
    PostFieldElement,
    PrevElement,
    RefreshElement,
)
from warp.representation.variables import SetVarElement, TimerElement

from html_render.link_creator import ProxiLinkCreator


class RenderToHtml:
    def __init__(self, card: Card, link_creator: ProxiLinkCreator):
        self.card = card
        self.link_creator = link_creator

    def generate(self) -> str:
        root = ET.Element("div", attrib={"class": "card-content"})
        for element in self.card.children:
            self._render_node(root, element)
        return ET.tostring(root, encoding="unicode")

    def _render_node(self, parent: ET.Element, node) -> None:
        if isinstance(node, str):
            self._append_text(parent, node)
            return

        if isinstance(node, dict):
            if "name" in node and "options" in node:
                self._render_select(parent, node)
                return
            elif "value" in node and "content" in node:
                self._render_option(parent, node)
                return

        node_type_name = type(node).__name__

        match node_type_name:
            case "ParagraphHtmlElement":
                self._render_paragraph(parent, node)
            case "TextContent":
                self._append_text(parent, node.content)
            case "StrongTextHtmlElement":
                self._render_strong(parent, node)
            case "ItalicTextElement":
                self._render_italic(parent, node)
            case "BoldTextHtmlElement":
                self._render_bold(parent, node)
            case "SmallTextHtmlElement":
                self._render_small(parent, node)
            case "BigTextHtmlElement":
                self._render_big(parent, node)
            case "UnderlineTextElement":
                self._render_underline(parent, node)
            case "PreformattedText":
                self._render_pre(parent, node)
            case "BreakHtmlElement":
                ET.SubElement(parent, "br")
            case "TableElement":
                self._render_table(parent, node)
            case "AHtmlElement":
                self._render_a(parent, node)
            case "AnchorElement":
                self._render_anchor(parent, node)
            case "Image":
                self._render_image(parent, node)
            case "Input":
                self._render_input(parent, node)
            case "OptionGroup":
                self._render_option_group(parent, node)
            case "FieldSet":
                self._render_fieldset(parent, node)
            case "Do":
                self._render_do(parent, node)
            case "GoElement":
                self._render_go(parent, node)
            case "PrevElement":
                self._render_prev(parent, node)
            case "RefreshElement":
                self._render_refresh(parent, node)
            case "NoOpElement" | "PostFieldElement" | "OnPick":
                pass
            case "SetVarElement":
                self._render_setvar(parent, node)
            case "TimerElement":
                self._render_timer(parent, node)
            case "OnEvent":
                self._render_onevent(parent, node)
            case _:
                if hasattr(node, "children") and getattr(node, "children"):
                    for child in node.children:
                        self._render_node(parent, child)
                elif hasattr(node, "content") and getattr(node, "content"):
                    self._append_text(parent, getattr(node, "content"))
                else:
                    print(f"Unsupported tag! {node}", file=sys.stderr)

    def _append_text(self, parent: ET.Element, text: str) -> None:
        if not text:
            return
        if len(parent) > 0:
            last = parent[-1]
            last.tail = (last.tail or "") + text
        else:
            parent.text = (parent.text or "") + text

    def _render_paragraph(self, parent: ET.Element, paragraph: ParagraphHtmlElement) -> ET.Element:
        p_attrs = {}
        align = getattr(paragraph, "_align", None) or getattr(paragraph, "align", None)
        if align:
            align_val = getattr(align, "value", str(align))
            if align_val in ("left", "right", "center"):
                p_attrs["style"] = f"text-align: {align_val};"
        
        p = ET.SubElement(parent, "p", attrib=p_attrs)
        if hasattr(paragraph, "children") and paragraph.children:
            for child in paragraph.children:
                self._render_node(p, child)
        return p

    @staticmethod
    def _align_style_for_column(alignment: ColumnAlignment) -> str:
        align_val = getattr(alignment, "value", str(alignment))
        if align_val == "right":
            return "text-align: right;"
        elif align_val == "center":
            return "text-align: center;"
        return "text-align: left;"

    def _render_table(self, parent: ET.Element, table: TableElement) -> ET.Element:
        tbl = ET.SubElement(parent, "table", attrib={"border": "1", "cellpadding": "4", "cellspacing": "0"})
        if hasattr(table, "rows") and table.rows:
            for row in table.rows:
                tr = ET.SubElement(tbl, "tr")
                if hasattr(row, "columns") and row.columns:
                    for col_idx, col in enumerate(row.columns):
                        align_style = ""
                        if hasattr(table, "column_alignment"):
                            align_style = self._align_style_for_column(table.column_alignment(col_idx))
                        td = ET.SubElement(tr, "td", attrib={"style": align_style} if align_style else {})
                        if isinstance(col, TableColumn) and hasattr(col, "content"):
                            td.text = col.content
                        elif isinstance(col, str):
                            td.text = col
                        elif hasattr(col, "children"):
                            for child in col.children:
                                self._render_node(td, child)
        return tbl

    def _render_a(self, parent: ET.Element, a_elem: AHtmlElement) -> ET.Element:
        href = getattr(a_elem, "href", "")
        proxi_href = self.link_creator.create_for_url(href)
        a = ET.SubElement(parent, "a", attrib={"href": proxi_href})
        if hasattr(a_elem, "content") and a_elem.content:
            a.text = a_elem.content
        elif hasattr(a_elem, "children") and a_elem.children:
            for child in a_elem.children:
                self._render_node(a, child)
        return a

    def _render_anchor(self, parent: ET.Element, anchor: AnchorElement) -> ET.Element:
        span = ET.SubElement(parent, "span", attrib={"class": "wml-anchor"})
        if hasattr(anchor, "children") and anchor.children:
            for child in anchor.children:
                self._render_node(span, child)
        return span

    def _render_strong(self, parent: ET.Element, elem: StrongTextHtmlElement) -> ET.Element:
        strong = ET.SubElement(parent, "strong")
        self._render_text_elem_content(strong, elem)
        return strong

    def _render_italic(self, parent: ET.Element, elem: ItalicTextElement) -> ET.Element:
        italic = ET.SubElement(parent, "i")
        self._render_text_elem_content(italic, elem)
        return italic

    def _render_bold(self, parent: ET.Element, elem: BoldTextHtmlElement) -> ET.Element:
        bold = ET.SubElement(parent, "b")
        self._render_text_elem_content(bold, elem)
        return bold

    def _render_small(self, parent: ET.Element, elem: SmallTextHtmlElement) -> ET.Element:
        small = ET.SubElement(parent, "small")
        self._render_text_elem_content(small, elem)
        return small

    def _render_big(self, parent: ET.Element, elem: BigTextHtmlElement) -> ET.Element:
        big = ET.SubElement(parent, "big")
        self._render_text_elem_content(big, elem)
        return big

    def _render_underline(self, parent: ET.Element, elem: UnderlineTextElement) -> ET.Element:
        u = ET.SubElement(parent, "u")
        self._render_text_elem_content(u, elem)
        return u

    def _render_pre(self, parent: ET.Element, elem: PreformattedText) -> ET.Element:
        pre = ET.SubElement(parent, "pre")
        self._render_text_elem_content(pre, elem)
        return pre

    def _render_text_elem_content(self, parent: ET.Element, elem) -> None:
        if hasattr(elem, "content") and elem.content:
            parent.text = elem.content
        elif hasattr(elem, "children") and elem.children:
            for child in elem.children:
                self._render_node(parent, child)

    def _render_image(self, parent: ET.Element, img: Image) -> ET.Element:
        src = getattr(img, "src", "")
        alt = getattr(img, "alt", "image")
        attribs = {"src": src, "alt": alt}

        align = getattr(img, "align", None)
        if align:
            align_val = getattr(align, "value", str(align))
            if align_val in ("top", "middle", "bottom"):
                attribs["align"] = align_val

        img_elem = ET.SubElement(parent, "img", attrib=attribs)
        return img_elem

    def _render_input(self, parent: ET.Element, inp: Input) -> ET.Element:
        name = getattr(inp, "name", "")
        val = getattr(inp, "value", "")
        attribs = {"type": "text", "name": name, "value": val}
        size = getattr(inp, "size", -1)
        if isinstance(size, int) and size > 0:
            attribs["size"] = str(size)
        return ET.SubElement(parent, "input", attrib=attribs)

    def _render_select(self, parent: ET.Element, sel: dict) -> ET.Element:
        name = sel.get("name", "")
        select_elem = ET.SubElement(parent, "select", attrib={"name": name})
        options = sel.get("options", [])
        for opt in options:
            self._render_node(select_elem, opt)
        return select_elem

    def _render_option(self, parent: ET.Element, opt: dict) -> ET.Element:
        val = opt.get("value", "")
        opt_elem = ET.SubElement(parent, "option", attrib={"value": val})
        content = opt.get("content", "")
        if content:
            opt_elem.text = content
        return opt_elem

    def _render_option_group(self, parent: ET.Element, optgroup: OptionGroup) -> ET.Element:
        label = getattr(optgroup, "title", getattr(optgroup, "label", "Group"))
        grp_elem = ET.SubElement(parent, "optgroup", attrib={"label": label})
        if hasattr(optgroup, "children") and optgroup.children:
            for child in optgroup.children:
                self._render_node(grp_elem, child)
        return grp_elem

    def _render_fieldset(self, parent: ET.Element, fieldset) -> ET.Element:
        title = getattr(fieldset, "title", "")
        fs = ET.SubElement(parent, "fieldset")
        if title:
            leg = ET.SubElement(fs, "legend")
            leg.text = title
        if hasattr(fieldset, "children") and fieldset.children:
            for child in fieldset.children:
                self._render_node(fs, child)
        return fs

    def _render_do(self, parent: ET.Element, do_node: Do) -> ET.Element:
        label = getattr(do_node, "label", getattr(do_node, "type", "Action"))
        btn = ET.SubElement(parent, "button", attrib={"type": "button", "class": "wml-do-btn"})
        btn.text = label
        if hasattr(do_node, "children") and do_node.children:
            for child in do_node.children:
                self._render_node(btn, child)
        return btn

    def _render_go(self, parent: ET.Element, go: GoElement) -> ET.Element:
        href = getattr(go, "href", "")
        proxi_href = self.link_creator.create_for_url(href)
        a = ET.SubElement(parent, "a", attrib={"href": proxi_href, "class": "wml-action-go"})
        a.text = "Go"
        return a

    def _render_prev(self, parent: ET.Element, prev: PrevElement) -> ET.Element:
        a = ET.SubElement(parent, "a", attrib={"href": "javascript:history.back()", "class": "wml-action-prev"})
        a.text = "Back"
        return a

    def _render_refresh(self, parent: ET.Element, refresh: RefreshElement) -> ET.Element:
        a = ET.SubElement(parent, "a", attrib={"href": "javascript:location.reload()", "class": "wml-action-refresh"})
        a.text = "Refresh"
        return a

    def _render_setvar(self, parent: ET.Element, setvar: SetVarElement) -> ET.Element:
        name = getattr(setvar, "name", "")
        val = getattr(setvar, "value", "")
        return ET.SubElement(parent, "input", attrib={"type": "hidden", "name": name, "value": val})

    def _render_timer(self, parent: ET.Element, timer: TimerElement) -> ET.Element:
        val = str(getattr(timer, "value", "0"))
        return ET.SubElement(parent, "input", attrib={"type": "hidden", "class": "wml-timer", "value": val})

    def _render_onevent(self, parent: ET.Element, onevent: OnEvent) -> None:
        evt_type = getattr(onevent, "type", "")
        action = getattr(onevent, "action", None)
        if action:
            div = ET.SubElement(parent, "div", attrib={"class": f"wml-onevent wml-onevent-{evt_type}"})
            self._render_node(div, action)