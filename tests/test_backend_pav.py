"""Unit tests for the PAV backend in Annif"""

import logging
import annif.backend
import annif.corpus


def test_pav_default_params(datadir, document_corpus, project, caplog):
    logger = annif.logger
    logger.propagate = True
    caplog.set_level(logging.DEBUG)

    pav_type = annif.backend.get_backend("pav")
    pav = pav_type(
        backend_id='pav',
        params={},
        datadir=str(datadir))

    expected_default_params = {
        'min-docs': 10,
    }
    expected_msg = "all parameters not set, using following defaults:"
    assert expected_msg in caplog.records[0].message
    actual_params = pav.params
    for param, val in expected_default_params.items():
        assert param in actual_params and actual_params[param] == str(val)


def test_pav_train(app, datadir, tmpdir, project):
    pav_type = annif.backend.get_backend("pav")
    pav = pav_type(
        backend_id='pav',
        params={'limit': 50, 'min-docs': 2, 'sources': 'dummy-fi'},
        datadir=str(datadir))

    tmpfile = tmpdir.join('document.tsv')
    tmpfile.write("dummy\thttp://example.org/dummy\n" +
                  "another\thttp://example.org/dummy\n" +
                  "none\thttp://example.org/none")
    document_corpus = annif.corpus.DocumentFile(str(tmpfile))

    with app.app_context():
        pav.train(document_corpus, project)
    assert datadir.join('pav-model-dummy-fi').exists()
    assert datadir.join('pav-model-dummy-fi').size() > 0


def test_pav_initialize(app, datadir):
    pav_type = annif.backend.get_backend("pav")
    pav = pav_type(
        backend_id='pav',
        params={'limit': 50, 'min-docs': 2, 'sources': 'dummy-fi'},
        datadir=str(datadir))

    assert pav._models is None
    with app.app_context():
        pav.initialize()
    assert pav._models is not None
    # initialize a second time - this shouldn't do anything
    with app.app_context():
        pav.initialize()


def test_pav_suggest(app, datadir, project):
    pav_type = annif.backend.get_backend("pav")
    pav = pav_type(
        backend_id='pav',
        params={'limit': 50, 'min-docs': 2, 'sources': 'dummy-fi'},
        datadir=str(datadir))

    results = pav.suggest("""Arkeologiaa sanotaan joskus myös
        muinaistutkimukseksi tai muinaistieteeksi. Se on humanistinen tiede
        tai oikeammin joukko tieteitä, jotka tutkivat ihmisen menneisyyttä.
        Tutkimusta tehdään analysoimalla muinaisjäännöksiä eli niitä jälkiä,
        joita ihmisten toiminta on jättänyt maaperään tai vesistöjen
        pohjaan.""", project)

    assert len(pav._models['dummy-fi']) == 1
    assert len(results) > 0
