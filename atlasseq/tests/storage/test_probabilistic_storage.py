from atlasseq.tests.base import ST_KMER
from atlasseq.tests.base import ST_SAMPLE_NAME
from atlasseq.tests.base import ST_GRAPH
from atlasseq.tests.base import ST_BINARY_KMERS
from atlasseq.tests.base import ST_SAMPLE_COLOUR
from atlasseq.tests.base import REDIS_CLUSTER_STORAGE
from hypothesis import given
import hypothesis.strategies as st
from atlasseq.storage.graph.probabilistic import ProbabilisticInMemoryStorage
from atlasseq.storage.graph.probabilistic import ProbabilisticRedisHashStorage
from atlasseq.storage.graph.probabilistic import ProbabilisticRedisBitArrayStorage
from atlasseq.storage.graph.probabilistic import ProbabilisticBerkeleyDBStorage
from atlasseq.storage.graph.probabilistic import ProbabilisticLevelDBStorage
import os

POSSIBLE_STORAGES = [
    # ProbabilisticInMemoryStorage(),
    # ProbabilisticRedisHashStorage(REDIS_STORAGE),
    ProbabilisticRedisBitArrayStorage(REDIS_CLUSTER_STORAGE),
    # ProbabilisticBerkeleyDBStorage({'filename': './db'}),
]
ST_STORAGE = st.sampled_from(POSSIBLE_STORAGES)


@given(storage=ST_STORAGE, colour=ST_SAMPLE_COLOUR, element=ST_KMER,
       bloom_filter_size=st.integers(10000, 1000000),
       num_hashes=st.integers(min_value=1, max_value=5))
def test_add_contains(storage, colour, element, bloom_filter_size,  num_hashes):
    storage.bloom_filter_size = bloom_filter_size
    storage.num_hashes = num_hashes
    storage.delete_all()

    storage.bloomfilter.add(element, colour)
    assert storage.bloomfilter.contains(element, colour)
    assert not storage.bloomfilter.contains(element + "a", colour)


@given(storage=ST_STORAGE, colour=ST_SAMPLE_COLOUR, elements=st.lists(ST_KMER),
       bloom_filter_size=st.integers(10000, 1000000),
       num_hashes=st.integers(min_value=1, max_value=5))
def test_update_contains(storage, colour, elements, bloom_filter_size,  num_hashes):
    storage.bloom_filter_size = bloom_filter_size
    storage.num_hashes = num_hashes
    storage.delete_all()

    storage.bloomfilter.update(elements, colour)
    for k in elements:
        assert storage.bloomfilter.contains(k, colour)


@given(storage=ST_STORAGE, colour1=ST_SAMPLE_COLOUR, colour2=ST_SAMPLE_COLOUR,
       element=ST_KMER,
       bloom_filter_size=st.integers(10000, 1000000),
       num_hashes=st.integers(min_value=1, max_value=5))
def test_add_lookup(storage, colour1, colour2, element, bloom_filter_size,  num_hashes):
    storage.bloom_filter_size = bloom_filter_size
    storage.num_hashes = num_hashes
    storage.delete_all()
    if not colour1 == colour2:
        storage.bloomfilter.add(element, colour1)
        assert storage.bloomfilter.contains(element, colour1)
        assert not storage.bloomfilter.contains(element, colour2)
        assert storage.bloomfilter.lookup(element).getbit(colour1) == True
        assert storage.bloomfilter.lookup(element).getbit(colour2) == False

        storage.bloomfilter.add(element, colour2)
        assert storage.bloomfilter.contains(element, colour1)
        assert storage.bloomfilter.contains(element, colour2)
        assert storage.bloomfilter.lookup(element).getbit(colour1) == True
        assert storage.bloomfilter.lookup(element).getbit(colour2) == True


@given(storage=ST_STORAGE, colour1=ST_SAMPLE_COLOUR, colour2=ST_SAMPLE_COLOUR,
       elements=st.lists(ST_KMER, min_size=1),
       bloom_filter_size=st.integers(10000, 1000000),
       num_hashes=st.integers(min_value=1, max_value=5))
def test_add_lookup_list(storage, colour1, colour2, elements, bloom_filter_size,  num_hashes):
    storage.bloom_filter_size = bloom_filter_size
    storage.num_hashes = num_hashes
    storage.delete_all()
    if not colour1 == colour2:
        storage.bloomfilter.update(elements, colour1)
        assert all([storage.bloomfilter.contains(element, colour1)
                    for element in elements])
        assert all([not storage.bloomfilter.contains(element, colour2)
                    for element in elements])
        assert all([storage.bloomfilter.lookup(elements)[i].getbit(colour1)
                    for i in range(len(elements))]) == True
        assert all([storage.bloomfilter.lookup(elements)[i].getbit(colour2) == False
                    for i in range(len(elements))])

        storage.bloomfilter.update(elements, colour2)
        assert all([storage.bloomfilter.contains(element, colour1)
                    for element in elements])
        assert all([storage.bloomfilter.contains(element, colour2)
                    for element in elements])
        assert all([storage.bloomfilter.lookup(elements)[i].getbit(
            colour1) == True for i in range(len(elements))])
        assert all([storage.bloomfilter.lookup(elements)[i].getbit(
            colour2) == True for i in range(len(elements))])
