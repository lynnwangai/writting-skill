import asyncio
import unittest

from scripts.paginate_article import (
    FlowUnit,
    Measurement,
    atomize_blocks,
    assemble_units,
    pack_atom_pages,
    paginate_segment,
    rebalance_tail,
    split_plain_sentences,
)
from scripts.render_article import AUTHOR_SIGNOFF_MARKER


class PaginationTests(unittest.TestCase):
    def test_plain_prose_splits_only_at_sentence_boundaries(self):
        self.assertEqual(
            split_plain_sentences("第一句。第二句！第三句？"),
            ["第一句。", "第二句！", "第三句？"],
        )
        self.assertEqual(split_plain_sentences("**整段重点。不要拆。**"), ["**整段重点。不要拆。**"])
        self.assertEqual(split_plain_sentences("- 列表项目。不要拆。"), ["- 列表项目。不要拆。"])

    def test_heading_is_kept_with_first_following_sentence(self):
        atoms = atomize_blocks(["# 标题", "第一句。第二句。", "下一段。"])
        self.assertEqual([unit.text for unit in atoms[0]], ["# 标题", "第一句。"])
        self.assertEqual([unit.text for unit in atoms[1]], ["第二句。"])

    def test_author_signoff_marker_is_kept_with_following_blockquote(self):
        self.assertEqual(split_plain_sentences(AUTHOR_SIGNOFF_MARKER), [AUTHOR_SIGNOFF_MARKER])
        atoms = atomize_blocks([AUTHOR_SIGNOFF_MARKER, "> 作者介绍。"])
        self.assertEqual(
            [unit.text for unit in atoms[0]],
            [AUTHOR_SIGNOFF_MARKER, "> 作者介绍。"],
        )

    def test_assembly_preserves_paragraph_boundaries(self):
        units = [
            FlowUnit("第一句。", 1),
            FlowUnit("第二句。", 1),
            FlowUnit("下一段。", 2),
        ]
        self.assertEqual(assemble_units(units), "第一句。第二句。\n\n下一段。")

    def test_pagination_greedily_fills_real_measurement_capacity(self):
        atoms = atomize_blocks(["第一句。第二句。第三句。第四句。"])

        async def measure(markdown):
            return len(markdown.replace("\n", "")) <= 8

        pages = asyncio.run(paginate_segment(atoms, measure))
        self.assertEqual([assemble_units(page) for page in pages], ["第一句。第二句。", "第三句。第四句。"])

    def test_sparse_segment_tail_is_rebalanced_deterministically(self):
        atoms = [(FlowUnit("xx", block_id),) for block_id in range(12)]

        async def measure(markdown):
            used = markdown.count("x")
            return Measurement(fits=used <= 10, fill_ratio=used / 10)

        async def run():
            greedy = await pack_atom_pages(atoms, measure)
            self.assertEqual([len(page) for page in greedy], [5, 5, 2])
            return await rebalance_tail(greedy, measure, minimum_fill=0.75)

        balanced = asyncio.run(run())
        self.assertEqual([len(page) for page in balanced], [4, 4, 4])


if __name__ == "__main__":
    unittest.main()
