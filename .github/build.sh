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
    poetry run torchinstall $1
    poetry run jaxinstall $1
}

build $1
