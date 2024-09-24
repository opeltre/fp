from fp.meta import Functor, Monad
from fp.cartesian import Prod, Type


class WriterFunctor(Prod):
    """
    Base class for `Writer M` functors and monads.
    """

    _writer_: Type

    class Object(Prod.Object):
        """
        Wrap a value with a message.

        This class should expose the same interface as `Wrap.Object`
        as both implementations do morally the same thing.
        """

        @property
        def data(self):
            """Access raw value."""
            return self[1]

        @classmethod
        def cast(cls, data):
            print("Writer cast", data)
            return super().cast(data)

    @classmethod
    def new(cls, *As):
        return super().new(cls._writer_, *As)

    def _post_new_(WA, *As):
        WA._head_ = Prod
        WA._tail_ = (WA._writer_, *As)

    @classmethod
    def fmap(cls, *fs):
        id_W = Type.Hom.id(cls._writer_)
        Wf = Prod.fmap(id_W, *fs)
        return Wf

    @classmethod
    def _get_name_(cls, *As):
        return super()._get_name_(cls._writer_, *As)


class WriterMonad(WriterFunctor): ...


class Writer(Functor):
    """
    Constructor of `Writer` functors.

    Given a writing type `W`, the functor `Writer W` maps any
    type `A` to the pair type `(W, A)`.

    When `W` is a monoid, the functor `Writer W` is also a monad:

        unit : A -> (W, A)
             | a -> (1, a)

        join : (W, (W, A)) -> (W, A)
             | (v, (w, a)) -> (v `op` w, a)

    A particular example is `Str`, which is useful for writing logs
    or error messages.
    """

    _default_ = WriterFunctor

    def __new__(cls, W: type, bases=(), dct=None):
        if isinstance(W, Monoid):
            bases = (WriterMonad, *bases)
        if not len(bases):
            bases = (cls._default_,)
        dct = dict(_writer_=W)
        Writer_W = super().__new__(cls, f"({W}, ...)", bases, dct)
        return Writer_W
