"use strict";

const e = React.createElement;

class PhotosData extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoaded: false,
      items: null,
      allowTags: true,
      allowButtons: true
    };

    this.discardPhoto = this.discardPhoto.bind(this);
    this.addToPhotoStream = this.addToPhotoStream.bind(this);
    this.addTags = this.addTags.bind(this);
    this.updateTitle = this.updateTitle.bind(this);
  }

  checkInput(input_string) {
    function checkTags(tags) {
      const forbidden = ["\\", "/", "%"];
      let arr = tags.split(",");
      let safe = true;

      // for each value in arr check each char against the forbidden values
      for (var i = 0; i < arr.length; i++) {
        console.log(arr[i]);
        forbidden.forEach(char => {
          if (arr[i].includes(char)) {
            safe = false;
          }
        });

        if (arr[i].replace(/ /g, "").length < 1) {
          safe = false;
        }
      }

      if (arr.join("").replace(/,/g, "") < 1) {
        safe = false;
      }

      return safe;
    }
    return checkTags(input_string);
  }

  componentWillMount() {
    fetch("/api/uploaded")
      .then(res => res.json())
      .then(
        result => {
          // console.log("result", result);
          this.setState({
            isLoaded: true,
            items: result.photos
          });
        },
        error => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      );
  }

  discardPhoto(photo_id, key) {
    console.log("clicked discard", photo_id);

    let test = JSON.stringify({
      photoId: photo_id
    });

    console.log(test);

    fetch("/api/discard", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        photoId: photo_id
      })
    }).then(Response => {
      console.log("Response", Response.status);

      if (Response.status === 200) {
        let objectCopy = this.state.items;
        delete objectCopy[key];
        this.setState({
          items: objectCopy
        });
        console.log("getting here ok");
        console.log(this.state.items);
      }
    });
  }

  updateTitle(e, photo_id, key) {
    const new_title = e.target.value;

    fetch("/api/uploaded/title", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        photoId: photo_id,
        title: new_title
      })
    }).then(Response => {
      console.log(Response.status);
      if (Response.status === 200) {
        let objectCopy = this.state.items;
        objectCopy[key]["photo_title"] = new_title;
        this.setState({
          items: objectCopy
        });
      }
    });
  }

  addTags(e, photo_id) {
    if (e.target.value) {
      if (this.checkInput(e.target.value)) {
        this.setState({
          allowTags: true,
          allowButtons: true
        });

        fetch("/api/add/tags", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            photoId: photo_id,
            tagValues: e.target.value
          })
        }).then(Response => {
          console.log("Response", Response.status);

          if (Response.status === 200) {
            console.log(Response);
            // let objectCopy = this.state.items;
          }
        });
      } else {
        console.log("checkTags returned False");
        this.setState({
          allowTags: false,
          allowButtons: false
        });
      }
    } else {
      console.log("no tag value?");
      this.setState({
        allowTags: true,
        allowButtons: false
      });
    }
  }

  addToPhotoStream() {
    if (this.state.allowButtons) {
      console.log("hello from addToPhotoStream");
      // send data to the backend
      console.log(this.state.items);
      fetch("/api/upload/photostream", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          photos: this.state.items
        })
      }).then(Response => {
        window.location.assign(`/`);
      });
    }
  }

  addToNewAlbum() {
    console.log("hello from addToNewAlbum");
    // it just needs to direct to a new page
    window.location.assign(`/api/create/album`);
  }

  addToExistingAlbum() {
    console.log("hello from addToExistingAlbum");
    window.location.assign(`/api/select/album`);
  }

  warningArea() {
    return (
      <div className="row">
        <div className="col text-center">
          <div id="warning-text" className="alert alert-warning" role="alert">
            Tags may not be spaces and may not contain the characters: \ / %.
            Please check your tags and try again.
          </div>
        </div>
      </div>
    );
  }

  render() {
    let photo = null;
    let discardPhoto = this.discardPhoto;
    let updateTitle = this.updateTitle;
    let addTags = this.addTags;
    // onClick handlers for buttons
    let addToPhotoStream = this.addToPhotoStream;
    let addToNewAlbum = this.addToNewAlbum;
    let addToExistingAlbum = this.addToExistingAlbum;

    // safeguards against wrong input and warnings
    let allowTags = this.state.allowTags;
    let allowButtons = this.state.allowButtons;
    const warningArea = this.warningArea;

    if (this.state.items) {
      let photos = this.state.items;
      // console.log(photos);
      let photo = Object.keys(photos).map(function(key) {
        // let photo_url = photos[key]["original"];
        let photo_id = photos[key]["photo_id"];
        // console.log(photo_url);
        return (
          <div key={photos[key]["photo_id"]}>
            <div className="row">
              <div className="col my-auto">
                <img
                  src={photos[key]["original"]}
                  alt="Uploaded photo"
                  className="img-fluid"
                />
              </div>
              <div className="col text-center my-auto">
                <h5>Enter a title</h5>
                <input
                  className="input-group input-group-text"
                  type="text"
                  placeholder={
                    photos[key]["photo_title"] === null
                      ? ""
                      : photos[key]["photo_title"]
                  }
                  onBlur={e => updateTitle(e, photo_id, key)}
                  // disabled={!allowTags}
                />
                <hr />
                <h5>Enter tags below</h5>
                <p>
                  You can enter multiple tags seperating them with commas. Tags
                  may contain spaces, but a space itself cannot be a tag.
                </p>
                {allowTags === false ? warningArea() : null}
                <input
                  className="input-group input-group-text"
                  type="text"
                  onBlur={e => addTags(e, photo_id, key)}
                  placeholder={
                    photos[key]["tags"] === null ? "" : photos[key]["tags"]
                  }
                  defaultValue={
                    photos[key]["tags"] === null ? "" : photos[key]["tags"]
                  }
                  // disabled={!allowTitle}
                />
                <hr />
                <div className="row">
                  <div className="col">
                    <button
                      className="btn btn-danger btn-lg"
                      onClick={() => discardPhoto(photo_id, key)}
                    >
                      Discard photo
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <hr />
          </div>
        );
      });

      return (
        <div>
          {photo}

          <div className="row">
            <div className="col text-center">
              <button
                disabled={!allowButtons}
                className="btn btn-warning btn-block btn-lg"
                onClick={() => addToNewAlbum()}
              >
                Add to a new album
              </button>
            </div>

            <div className="col text-center">
              <button
                disabled={!allowButtons}
                className="btn btn-success btn-block btn-lg"
                onClick={() => addToPhotoStream()}
              >
                Add to photostream only
              </button>
            </div>

            <div className="col text-center">
              <button
                disabled={!allowButtons}
                className="btn btn-success btn-block btn-lg"
                onClick={() => addToExistingAlbum()}
              >
                Add to existing album
              </button>
            </div>
          </div>
          <hr />
        </div>
      );
    }

    return (
      <div>
        <h1>Hi from React</h1>

        {photo}
      </div>
    );
  }
}

const domContainer = document.querySelector("#upload-editor");
ReactDOM.render(e(PhotosData), domContainer);
