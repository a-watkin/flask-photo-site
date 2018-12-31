"use strict";

const e = React.createElement;

class PhotoSelector extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      currentOffset: 20,
      selectedPhotos: [],
      albumId: null
    };

    this.photoClick = this.photoClick.bind(this);
  }

  componentWillMount() {
    // getting the album id from the URL
    let currentUrl = window.location.href;
    let splitUrl = currentUrl.split("/");
    const albumId = splitUrl[5];

    fetch("/api/getphotos", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(
        result => {
          // console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos,
            currentOffset: result.offset,
            albumId: albumId
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
    // console.log("next called ", this.state.currentOffset);

    fetch(`/api/getphotos?offset=${this.state.currentOffset + 20}`, {
      credentials: "include"
    })
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

  getPreviousPhotos() {
    // console.log("previous called ", this.state.currentOffset);

    if (this.state.currentOffset <= 0) {
      return false;
    }

    fetch(`/api/getphotos?offset=${this.state.currentOffset - 20}`, {
      credentials: "include"
    })
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

  sendData() {
    console.log("getting here?", this.state.albumId, this.state.selectedPhotos);
    // /api/getphotos
    fetch("/api/getphotos", {
      method: "POST",
      credentials: "include",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        albumId: this.state.albumId,
        photos: this.state.selectedPhotos
      })
    }).then(() => {
      // redirect after successful post
      console.log(this.state);
      window.location.assign(`/albums/${this.state.albumId}`);
    });
  }

  photoClick(photo_id) {
    // console.log("Greetings from photoClick the photo_id is ", photo_id);

    // only add the photo_id if it's not in the array
    if (!this.state.selectedPhotos.includes(photo_id)) {
      this.state.selectedPhotos.push(photo_id);
    } else {
      // remove the photo from the array
      let tempAray = [...this.state.selectedPhotos];
      let index = tempAray.indexOf(photo_id);
      if (index !== -1) {
        tempAray.splice(index, 1);
        this.setState({
          selectedPhotos: tempAray
        });
      }
    }

    // console.log("state of selectedPhotos ", this.state.selectedPhotos);
    // also not ideal but good enough for now
    this.forceUpdate();
  }

  render() {
    let cardStyle = {
      width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px"
    };

    let selectedCard = {
      width: "18rem",
      margin: "0 auto",
      float: "none",
      marginBottom: "10px",
      backgroundColor: "#28a745"
    };

    let selectedPhotos = this.state.selectedPhotos;
    let large_square = "";
    // it doesn't seemt to be able to get this reference
    // without delaring it here from the Objct.keys reurn statment
    // also passing it and invoking leads to it being executed twice?
    let photoClick = this.photoClick;

    if (this.state.items) {
      large_square = this.state.items[0]["large_square"];
      const photos = this.state.items;

      // console.log(this.state.items[0]["large_square"]);
      let test = Object.keys(photos).map(function(key, index) {
        return (
          <div key={photos[key]["photo_id"]} className="col text-right">
            <div
              id="photo-select"
              className="card"
              // not ideal right here...but it works
              onClick={function(event) {
                photoClick(photos[key]["photo_id"]);
              }}
              style={
                selectedPhotos.includes(photos[key]["photo_id"])
                  ? selectedCard
                  : cardStyle
              }
            >
              <div className="card-header">
                <h5 className="card-title text-center">
                  {photos[key]["photo_title"]}
                </h5>
              </div>

              <div className="card-body">
                <img
                  src={photos[key]["large_square"]}
                  alt="Responsive image"
                  className="card-img-top img-fluid"
                />
              </div>
            </div>
          </div>
        );
      });

      // console.log("what is?", selectedPhotos);

      return (
        <div>
          <div className="row text-center">
            <div className="col">
              <button
                className="btn btn-block btn-lg"
                onClick={() => this.getPreviousPhotos()}
              >
                Next
              </button>
            </div>
            <div className="col">
              <button
                className="btn btn-block btn-lg"
                onClick={() => this.getNextPhotos()}
              >
                Previous
              </button>
            </div>
          </div>

          <hr />

          <div className="row"> {test} </div>

          <div className="row">
            <div className="col text-left">
              <a href="/edit/albums">
                <button className="btn btn-success btn-block btn-lg">
                  Return to edit albums
                </button>
              </a>
            </div>

            <div className="col text-right">
              <button
                type="submit"
                className="btn btn-warning btn-block btn-lg"
                onClick={() => this.sendData()}
              >
                Add photos
              </button>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="row">
        <div className="col">
          <h2> There was a problem getting data. </h2>
        </div>
      </div>
    );
  }
}

const domContainer = document.querySelector("#photos-selector");
ReactDOM.render(e(PhotoSelector), domContainer);
