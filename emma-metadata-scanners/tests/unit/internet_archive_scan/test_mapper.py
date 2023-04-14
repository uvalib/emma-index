from internet_archive_shared import metadata

my_map = [{'name': '__ia_thumb.jpg', 'source': 'original', 'mtime': '1565958074', 'size': '11365', 'format': 'Item Tile', 'rotation': '0', 'md5': '50fcd741cd8fa052209a5699008e67a6', 'crc32': '4df5d277', 'sha1': '098c450b8fe661aca11a312a3deb576f79108bfd'},
          {'name': 'francisbaconstud0000pepp.pdf', 'source': 'derivative', 'format': 'Text PDF', 'original': 'francisbaconstud0000pepp_abbyy.gz', 'mtime': '1565957613',
           'size': '15820345', 'md5': '7b08aea8bb77391f2bc3db132724f0a4', 'crc32': '3aba6f0d', 'sha1': '4f2b11721945e27f6d9d91e3f29959d598274327', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_abbyy.gz', 'source': 'derivative', 'format': 'Abbyy GZ', 'original': 'francisbaconstud0000pepp_jp2.zip', 'mtime': '1565954931',
           'size': '8298068', 'md5': 'c179e4e80e701dd95ebbd1b6b1b754f9', 'crc32': 'a882e6ac', 'sha1': '69ca59611b5455cd3acf66448926149c99438f59', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_dc.xml', 'source': 'original', 'format': 'Dublin Core', 'mtime': '1565947899', 'size': '1746',
           'md5': 'c72816bd3b1513d854fce705d59cf419', 'crc32': '5beaa52f', 'sha1': '4f8bcc9e1d84af12632efa62cba5b77d2157d7aa'},
          {'name': 'francisbaconstud0000pepp_djvu.txt', 'source': 'derivative', 'format': 'DjVuTXT', 'original': 'francisbaconstud0000pepp_djvu.xml', 'mtime': '1565958069',
           'size': '573240', 'md5': '3582333c6c8ae925048f66652b9e134b', 'crc32': 'af64005e', 'sha1': 'b5dd5a55c1ac1bf5aeb599270ba8e23263fefe6f', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_djvu.xml', 'source': 'derivative', 'format': 'Djvu XML', 'original': 'francisbaconstud0000pepp_abbyy.gz', 'mtime': '1565958060',
           'size': '5467612', 'md5': '1fccce78cf2d03f88dd1c7f404d3dff0', 'crc32': '53dae0cf', 'sha1': '1eda1f39ba57bd90cae165000fb86d5e4a048579', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_encrypted.epub', 'source': 'derivative', 'format': 'ACS Encrypted EPUB', 'original': 'francisbaconstud0000pepp_abbyy.gz',
           'mtime': '1565957785', 'size': '2349166', 'md5': 'ca1a53ef004aee58dfd089032ae4e247', 'crc32': 'f24cb138', 'sha1': '6a9c326297c194b7ca134c319532b27bcf4eb49e'},
          {'name': 'francisbaconstud0000pepp_encrypted.pdf', 'source': 'derivative', 'format': 'ACS Encrypted PDF', 'original': 'francisbaconstud0000pepp.pdf',
           'mtime': '1565958064', 'size': '15820992', 'md5': 'd8cb788b902b3b559b6644be84e24f51', 'crc32': '105f8649', 'sha1': '2969497cbaa0e9f879fca569fa55efe0c6c8f8ac'},
          {'name': 'francisbaconstud0000pepp_events.json', 'source': 'original', 'mtime': '1565947723', 'size': '57', 'md5': '9c65c0da56ea67528dc9e60622f4cf05',
           'crc32': 'fc94b18a', 'sha1': 'bebfaab7ac6b22544ef417f5d0f8ac33108de974', 'format': 'JSON', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_files.xml', 'source': 'original',
           'format': 'Metadata', 'md5': '1874008991702a98d14b5e1fd2daa947'},
          {'name': 'francisbaconstud0000pepp_jp2.zip', 'source': 'derivative', 'format': 'Single Page Processed JP2 ZIP', 'original': 'francisbaconstud0000pepp_orig_jp2.tar',
           'mtime': '1565953404', 'size': '139018796', 'md5': '9277ff890bce4d449b9428699790aee5', 'crc32': '4e8df1bc', 'sha1': 'e896aa25a0869f5cc49db995e5e4bcb307a38a4f', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_loans.json', 'source': 'original', 'mtime': '1579133808', 'size': '1515', 'format': 'JSON',
           'private': 'true', 'md5': 'b79c4e0c1cde5119890dfdd03ffc86c1', 'crc32': '823c3086', 'sha1': '9f26efedfdc1c1e5206f912718745703a5168613'},
          {'name': 'francisbaconstud0000pepp_marc.xml', 'source': 'original', 'mtime': '1565947899', 'size': '3320', 'format': 'MARC',
           'md5': '8d6b695eccebfd72fef6d95e8bf8a0a3', 'crc32': '749fde09', 'sha1': '68211e06861629bafae655935486fa57798b5275'},
          {'name': 'francisbaconstud0000pepp_meta.mrc', 'source': 'original', 'mtime': '1565753553', 'size': '1489',
           'md5': '4e2d2dd25bf4f09261941eab372eec90', 'crc32': '4c511f6d', 'sha1': '74d61f2533a6275640c0f03621a06c4f417e7a5e', 'format': 'MARC Binary'},
          {'name': 'francisbaconstud0000pepp_meta.sqlite', 'source': 'original', 'mtime': '1565947803', 'size': '19456', 'format': 'Metadata',
           'md5': '41ed9dd0dee02d9ea79cdee4a99abf2c', 'crc32': '0623935f', 'sha1': 'f91265c19fb1c547639160486ed88e0c35c940a6'},
          {'name': 'francisbaconstud0000pepp_meta.xml', 'source': 'original', 'mtime': '1579133808', 'size': '3656', 'format': 'Metadata',
           'md5': '956d0d0854f07a702d41c52ac8742480', 'crc32': '1eca1bcd', 'sha1': 'ed0e6fd535c3437fbd79b352d45d24db40e54efa'},
          {'name': 'francisbaconstud0000pepp_orig_jp2.tar', 'source': 'original', 'mtime': '1565947803', 'size': '591626240', 'format': 'Single Page Original JP2 Tar',
           'private': 'true', 'md5': 'cc2e957672c2f43211f679ddeb515808', 'crc32': 'd59cf9b2', 'sha1': '8240da243982d830424174f22af28a0762ca5da7'},
          {'name': 'francisbaconstud0000pepp_scandata.xml', 'source': 'original', 'mtime': '1565947803', 'size': '495229', 'format': 'Scandata',
           'md5': 'e2d42889e70ff86e5587b96072481326', 'crc32': '0e0642a7', 'sha1': 'd06e85ef0ab31ccaa587c3e45e7f29adc9ffe12f'},
          {'name': 'francisbaconstud0000pepp_slip.png', 'source': 'original', 'mtime': '1565751697', 'size': '37250', 'md5': 'b6cac6acabafe151abf4df4b97171b41',
           'crc32': 'af3a06b7', 'sha1': '0bd07829b8d197d5ef33ce3363f50e83932e86cf', 'format': 'PNG', 'private': 'true'},
          {'name': 'francisbaconstud0000pepp_slip_thumb.jpg', 'source': 'derivative', 'format': 'JPEG Thumb', 'original': 'francisbaconstud0000pepp_slip.png', 'mtime': '1565947902',
           'size': '5806', 'md5': '075623414bd1ffc7c500ea85247e2baa', 'crc32': '26a8e14b', 'sha1': '92a519f6bbaf1671e7b4c2bfecd3d288f25aea2c', 'private': 'true'},
          {'name': 'logs/francisbaconstud0000pepp_iabdash_2019-08-1411:32:29.log', 'source': 'original', 'mtime': '1565753558', 'size': '1342',
           'md5': 'ecff9645ecb491fb45bc8b26ffcfbc7e', 'crc32': '523c0bc4', 'sha1': '1835dd9d4579497d28963ae96559380bfda3169c', 'format': 'Log', 'private': 'true'},
          {'name': 'logs/francisbaconstud0000pepp_scanning_2019-08-1411:32:34.log', 'source': 'original', 'mtime': '1565753563', 'size': '699665', 'md5': '55de53eaa065d2dac3a2cdae41cf132e', 'crc32': 'ad895b61', 'sha1': '139c7d07f5f1027824305048c9c78d9c41475999', 'format': 'Log', 'private': 'true'}]


def test_get_format_file_map():
    new_map = metadata.get_format_file_map(my_map)
    assert len(new_map) > 0
    for key in new_map:
        assert len(new_map[key]['name']) > 0
