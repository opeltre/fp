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
    echo "> Install pip and poetry"
    echo "..."
    python -m pip install --upgrade pip
    python -m pip install pytest poetry poethepoet
    python -m pip install flake8-future-annotations
    echo "..."
    echo "> Build the fp backage"
    poetry install
    echo "..."
    if [[ $1 = *torch* ]]; then
        echo "> Install torch"
        poetry poe torchinstall
        echo "..."
    fi
    if [[ $1 = *jax* ]]; then
        echo "> Install jax"
        poetry poe jaxinstall
        echo "..."
    fi
}

function run_linter() {
    # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
}
