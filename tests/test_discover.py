"""Tests for course map discovery in organizer HTML."""

from collections import Counter
from pathlib import Path

import pytest

from race_courses.discover import (
    FETCHABLE,
    MYMAPS_KML,
    classify,
    find_course_links,
    find_sources,
    kind_for_content_type,
    source_ref,
)
from race_courses.models import SourceRef

FIXTURES = Path(__file__).parent / "fixtures" / "sources"
PAGE_URL = "https://example.com/course/"


def mymaps(mid: str) -> str:
    return MYMAPS_KML.format(mid=mid)


def test_fetchable_kinds() -> None:
    assert sorted(FETCHABLE) == ["gpx", "kml", "kmz", "mymaps"]


@pytest.mark.parametrize(
    ("url", "label", "kind"),
    [
        ("https://example.com/files/course.gpx", "", "gpx"),
        ("https://example.com/files/COURSE.KML?dl=1", "", "kml"),
        ("https://example.com/download?file=course.kmz", "", "kmz"),
        ("https://www.google.com/maps/d/embed?mid=abc-DEF_123&ehbc=2E312F", "", "mymaps"),
        ("https://www.google.com/maps/d/u/0/viewer?mid=abc", "", "mymaps"),
        ("https://www.google.com/maps/d/edit?mid=abc", "", "mymaps"),
        ("https://www.google.com/maps/d/kml?mid=abc&forcekml=1", "", "mymaps"),
        ("https://www.google.co.uk/maps/d/viewer?mid=abc", "", "mymaps"),
        ("https://www.google.com/maps/d/viewer", "", "googlemaps"),
        ("https://www.google.com/maps/place/Start+Line/@40.4,-79.9,15z", "", "googlemaps"),
        ("https://www.google.com/maps/embed?pb=!1m18", "", "googlemaps"),
        ("https://maps.google.com/maps?q=start+line&output=embed", "", "googlemaps"),
        ("https://maps.app.goo.gl/AbC123", "", "googlemaps"),
        ("https://goo.gl/maps/AbC123", "", "googlemaps"),
        ("https://www.strava.com/routes/3012345678901234567", "", "strava"),
        ("https://www.strava.com/activities/1234567890", "", "strava"),
        ("https://www.strava.com/segments/1234567", "", "strava"),
        ("https://ridewithgps.com/routes/44556677", "", "ridewithgps"),
        ("https://ridewithgps.com/routes/44556677.gpx", "", "ridewithgps"),
        ("https://ridewithgps.com/embeds?type=route&id=44556677", "", "ridewithgps"),
        ("https://www.mapmyrun.com/routes/view/5566778899", "", "mapmyrun"),
        ("https://connect.garmin.com/modern/course/123456789", "", "garmin"),
        ("https://connect.garmin.com/modern/activity/123456789", "", "garmin"),
        ("https://www.plotaroute.com/route/2233445", "", "plotaroute"),
        ("https://www.plotaroute.com/embedmap/2233445", "", "plotaroute"),
        ("https://racemap.com/player/example-marathon-2026", "", "racemap"),
        ("https://www.arcgis.com/apps/instant/basic/index.html?appid=abc123", "", "arcgis"),
        ("https://experience.arcgis.com/experience/abc123", "", "arcgis"),
        ("https://arcg.is/1AbCd", "", "arcgis"),
        ("https://onthegomap.com/s/abc12345", "", "onthegomap"),
        ("https://caltopo.com/m/ABCD1", "", "caltopo"),
        ("https://footpathapp.com/routes/0d4f0e7e-1234", "", "footpath"),
        ("https://example.com/docs/Course_Map_2026.pdf", "", "pdf"),
        ("https://example.com/docs/elevation.pdf", "Course details", "pdf"),
        ("https://example.com/docs/CourseMap2026.pdf", "", "pdf"),
        ("https://example.com/docs/waiver.pdf", "Waiver", None),
        ("https://example.com/logos/event.png", "Logo with overlaid text and maple leaf icons", None),
        ("https://example.com/icons/icon-plus.svg", "Course amenities", None),
        ("https://example.com/feed/placeholder.png", "Support at the finish line. " * 5 + "Cheer the course!", None),
        ("https://example.com/photos/IMG_2.jpg", "Support along the course", "image"),
        ("https://example.com/images/route-map.png", "", "image"),
        ("https://example.com/images/IMG_0001.jpg?w=800", "Course map", "image"),
        ("https://example.com/images/IMG_0001.jpg", "Finish line", None),
        ("https://example.com/register", "Course registration", None),
        ("https://www.strava.com/clubs/12345", "", None),
        ("https://racemap.com/", "", None),
        ("mailto:info@example.com", "course map", None),
        ("javascript:void(0)", "course.gpx", None),
        ("http://[bad-ipv6/course.gpx", "", None),
    ],
)
def test_classify(url: str, label: str, kind: str | None) -> None:
    assert classify(url, label) == kind


@pytest.mark.parametrize(
    ("content_type", "kind"),
    [
        ("application/pdf", "pdf"),
        ("image/jpeg", "image"),
        ("image/png", "image"),
        ("application/gpx+xml", "gpx"),
        ("application/vnd.google-earth.kml+xml", "kml"),
        ("application/vnd.google-earth.kmz", "kmz"),
        ("text/html", None),
        ("", None),
    ],
)
def test_kind_for_content_type(content_type: str, kind: str | None) -> None:
    assert kind_for_content_type(content_type) == kind


def test_source_ref_turns_my_maps_links_into_the_kml_export() -> None:
    ref = source_ref("https://www.google.com/maps/d/viewer?mid=abc123&ll=40,-80#top", "https://example.com/", " Map ")
    assert ref == SourceRef(kind="mymaps", url=mymaps("abc123"), found_on="https://example.com/", label="Map")


def test_source_ref_keeps_other_urls_without_their_fragment() -> None:
    ref = source_ref("https://example.com/files/course.gpx#download", "https://example.com/")
    assert ref == SourceRef(kind="gpx", url="https://example.com/files/course.gpx", found_on="https://example.com/")


def test_source_ref_returns_none_for_other_urls() -> None:
    assert source_ref("https://example.com/register", "https://example.com/") is None
    assert source_ref("http://[bad", "https://example.com/") is None


def test_find_sources_finds_every_kind_on_a_messy_page() -> None:
    refs = find_sources((FIXTURES / "race_page.html").read_text(), PAGE_URL)
    assert len({ref.url for ref in refs}) == len(refs)
    assert all(ref.found_on == PAGE_URL for ref in refs)
    assert {(ref.kind, ref.url) for ref in refs} == {
        ("gpx", "https://example.com/files/course.gpx"),
        ("gpx", "https://example.com/files/course-2026.gpx"),
        ("kml", "https://example.com/course/files/course.kml"),
        ("kmz", "https://cdn.example.com/files/course-2026.kmz"),
        ("mymaps", mymaps("ANCHORMID456")),
        ("mymaps", mymaps("IFRAMEMID789")),
        ("mymaps", mymaps("JSONMID123")),
        ("mymaps", mymaps("THUMBMID000")),
        ("mymaps", mymaps("SCRIPTMID321")),
        ("pdf", "https://example.com/docs/Course_Map_2026.pdf"),
        ("pdf", "https://example.com/docs/elevation.pdf"),
        ("pdf", "https://example.com/docs/course-map.pdf"),
        ("pdf", "https://example.com/docs/route-map.pdf"),
        ("image", "https://example.com/images/map-overview.png"),
        ("image", "https://example.com/images/map-overview-thumb.png"),
        ("image", "https://static.example.com/uploads/course-map-2026.jpg"),
        ("strava", "https://www.strava.com/routes/3012345678901234567"),
        ("strava", "https://www.strava.com/routes/9988776655443322110/embed"),
        ("ridewithgps", "https://ridewithgps.com/routes/44556677"),
        ("ridewithgps", "https://ridewithgps.com/embeds?type=route&id=44556677&sampleGraph=true"),
        ("mapmyrun", "https://www.mapmyrun.com/routes/view/5566778899"),
        ("garmin", "https://connect.garmin.com/modern/course/123456789"),
        ("plotaroute", "https://www.plotaroute.com/route/2233445"),
        ("racemap", "https://racemap.com/player/example-marathon-2026"),
        ("arcgis", "https://www.arcgis.com/apps/instant/basic/index.html?appid=abc123"),
        ("onthegomap", "https://onthegomap.com/s/abc12345"),
        ("caltopo", "https://caltopo.com/m/ABCD1"),
        ("footpath", "https://footpathapp.com/routes/0d4f0e7e-1234"),
        ("googlemaps", "https://www.google.com/maps/place/Start+Line/@40.44,-79.99,15z"),
    }
    assert Counter(ref.kind for ref in refs)["mymaps"] == 5


def test_find_sources_keeps_document_order_and_link_labels() -> None:
    refs = find_sources((FIXTURES / "race_page.html").read_text(), PAGE_URL)
    labels = {ref.url: ref.label for ref in refs}
    assert refs[0].url == "https://example.com/files/course.gpx"
    assert labels["https://example.com/files/course.gpx"] == "GPX file"
    assert labels["https://example.com/docs/Course_Map_2026.pdf"] == "Printable map"
    assert labels[mymaps("ANCHORMID456")] == "Interactive map"
    assert labels["https://example.com/images/map-overview.png"] == "Course map overview"
    assert labels["https://www.strava.com/routes/9988776655443322110/embed"] == ""


def test_find_sources_reads_lazy_iframe_attributes() -> None:
    html = (
        '<iframe data-lazy-src="https://www.google.com/maps/d/embed?mid=LAZY1" src="about:blank"></iframe>'
        '<iframe data-src="https://www.strava.com/routes/123/embed"></iframe>'
        '<embed data-src="https://www.plotaroute.com/embedmap/99">'
    )
    refs = find_sources(html, PAGE_URL)
    assert [(ref.kind, ref.url) for ref in refs] == [
        ("mymaps", mymaps("LAZY1")),
        ("strava", "https://www.strava.com/routes/123/embed"),
        ("plotaroute", "https://www.plotaroute.com/embedmap/99"),
    ]


def test_find_sources_reads_embeds_hidden_in_escaped_json() -> None:
    squarespace = (
        '<div class="sqs-block embed-block" data-block-json="{&quot;html&quot;:&quot;&lt;iframe src=\\&quot;'
        "https://www.google.com/maps/d/embed?mid=SQSMID1&amp;amp;ehbc=2E312F\\&quot;&gt;&lt;/iframe&gt;&quot;}\"></div>"
    )
    wix = '<script>{"src":"https:\\/\\/static.wixstatic.com\\/ugd\\/abc_123.kmz?dn=course.kmz"}</script>'
    refs = find_sources(squarespace + wix, PAGE_URL)
    assert [(ref.kind, ref.url) for ref in refs] == [
        ("mymaps", mymaps("SQSMID1")),
        ("kmz", "https://static.wixstatic.com/ugd/abc_123.kmz"),
    ]


def test_find_sources_only_reports_images_that_look_like_course_maps() -> None:
    html = (
        '<img src="/photos/finish.jpg" alt="Finish line">'
        '<img src="/photos/IMG_1.jpg" alt="2026 course map">'
        '<img data-src="/uploads/Route-Map.webp" alt="">'
    )
    assert [(ref.kind, ref.url, ref.label) for ref in find_sources(html, PAGE_URL)] == [
        ("image", "https://example.com/photos/IMG_1.jpg", "2026 course map"),
        ("image", "https://example.com/uploads/Route-Map.webp", ""),
    ]


def test_find_sources_labels_unnamed_files_with_their_section_heading() -> None:
    wix_image = "https://static.wixstatic.com/media/1994cc_3b5c~mv2.png/v1/fill/w_49,h_32,q_80/12kmapbb2_2x.png"
    html = (
        f'<h2>12k course map</h2><div><img src="{wix_image}" alt="12kmapbb2_2x.png"></div>'
        '<p>Download the PDF <a href="/_files/ugd/ba4a55_25f9.pdf">here</a>.</p>'
        '<h2>Sponsors</h2><img src="/logos/acme.png" alt="Acme"><a href="/_files/ugd/other.pdf">here</a>'
    )
    assert [(ref.kind, ref.url, ref.label) for ref in find_sources(html, PAGE_URL)] == [
        ("image", wix_image, "12k course map"),
        ("pdf", "https://example.com/_files/ugd/ba4a55_25f9.pdf", "12k course map"),
    ]


def test_find_sources_on_a_page_without_maps_is_empty() -> None:
    assert find_sources('<a href="/register">Register</a><img src="/logo.png" alt="Logo">', PAGE_URL) == []


def test_find_course_links_ranks_path_matches_above_text_matches() -> None:
    html = (FIXTURES / "homepage.html").read_text()
    assert find_course_links(html, "https://www.example.com/", limit=10) == [
        "https://www.example.com/race-info/course/",
        "https://example.com/maps/",
        "https://www.example.com/info/?page=route-map",
        "https://www.example.com/coursemap/",
        "https://www.example.com/event-details/",
        "https://www.example.com/faq/",
    ]


def test_find_course_links_honours_the_limit() -> None:
    html = (FIXTURES / "homepage.html").read_text()
    assert find_course_links(html, "https://www.example.com/", limit=2) == [
        "https://www.example.com/race-info/course/",
        "https://example.com/maps/",
    ]


def test_find_course_links_skips_self_files_sitemaps_and_other_sites() -> None:
    html = (FIXTURES / "homepage.html").read_text()
    links = find_course_links(html, "https://www.example.com/", limit=100)
    assert len(links) == 6
    unwanted_parts = ("sitemap", ".pdf", ".png", ".gpx", "other.example.org", "registration.example.com", "mailto")
    for unwanted in (*unwanted_parts, "maple", "kids-run"):
        assert not any(unwanted in link for link in links)
    assert "https://www.example.com/" not in links
