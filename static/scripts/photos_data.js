"use strict";

const e = React.createElement;

class PhotosData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      currentOffset: 20
    };
  }

  componentWillMount() {
    fetch("http://127.0.0.1:5000/api/getphotos")
      .then(res => res.json())
      .then(
        result => {
          // console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getNextPhotos() {
    console.log("next called ", this.state.currentOffset);

    fetch(
      `http://127.0.0.1:5000/api/getphotos?offset=${this.state.currentOffset +
        20}`
    )
      .then(res => res.json())
      .then(
        result => {
          console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  getPreviousPhotos() {
    console.log("previous called ", this.state.currentOffset);

    if (this.state.currentOffset <= 0) {
      return false;
    }

    fetch(
      `http://127.0.0.1:5000/api/getphotos?offset=${this.state.currentOffset -
        20}`
    )
      .then(res => res.json())
      .then(
        result => {
          console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  render() {
    let large_square = "";
    if (this.state.items) {
      large_square = this.state.items[0]["large_square"];
      const photos = this.state.items;

      console.log(this.state.items[0]["large_square"]);
      let test = Object.keys(photos).map(function(key, index) {
        // console.log();
        return (
          <div key={index}>
            <h5>{photos[key]["photo_title"]}</h5>
          </div>
        );
      });

      console.log(test);

      return (
        <div>
          <h1 className="text-center">FUCK YOU BITCHES</h1>

          <div className="row text-center">
            <div className="col">
              <button
                className="btn btn-lg"
                onClick={() => this.getPreviousPhotos()}
              >
                Next
              </button>
            </div>
            <div className="col">
              <button
                className="btn btn-lg"
                onClick={() => this.getNextPhotos()}
              >
                Previous
              </button>
            </div>
          </div>

          <img src={large_square} alt="" />
          {test}
        </div>
      );
    }

    if (this.state.items) {
      photo_id = this.state.items[0]["photo_id"];
    }

    return (
      <div className="row">
        <div className="col">
          <img src={large_square} alt="" />
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector("#like_button_container");
ReactDOM.render(e(PhotosData), domContainer);
