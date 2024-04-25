function torchinstall () {
    case $1 in
        cpu) 
            pip install torch --index-url https://download.pytorch.org/whl/cpu
            ;;
        [0-9|.]*) 
            pip install "torch==$1"
            ;;
    esac
}

function jaxinstall () {
    case $1 in 
        cpu) 
            pip install -U "jax[cpu]"
            ;;
        [0-9|.]*)
            pip install "jax==$1"
            ;;
    esac
}

function build() {
    poetry install
    poetry poe torchinstall
    poetry poe jaxinstall
}

build $1
